import pandas as pd
import performance_metrics
import numpy as np
from create_weighted_matrix import returnCorrectWeightedMatrix
from joblib import Parallel, delayed
from math import sqrt
from provide_adjuster import provide_adjuster
from geneticalgorithm2 import geneticalgorithm2  as ga
from datetime import datetime
from CA_dispersion import compute_hourly_dispersion
import json

def compute_mean_monthly_dispersion(raster, baselineNO2, TrafficNO2perhour, onroadindices, 
                                    weightmatrix, nr_repeats, adjuster=None, iter = True, 
                                    baseline = False, baseline_coeff = 1, traffemissioncoeff_onroad= 1,  
                                    traffemissioncoeff_offroad= 1):
    """Calculates the mean monthly dispersion of the traffic NO2 values for each hour. 
    The function uses the correct cellautom_dispersion function from the CA_dispersion module 
    depending on the arguments.

    Args:
        raster (xarray raster): the raster that is used for the dispersion model (xarray format (see package doc)) .
        baselineNO2 (vector(float)): The list of baseline NO2 values for each raster cell.
        TrafficNO2perhour (dataframe(float)): The dataframe with the hourly traffic NO2 values for each raster cell. Only the cells on roads should have values the rest default to 0.
        onroadindices (list(int)): A list of the indices of the cells that are on roads.
        weightmatrix (matrix(float)): the meteorologically defined weight matrix used for the focal operation
        nr_repeats (int): The number of times the focal operation is repeated.
        adjuster (list(float), optional): The adjuster values for each cell. Only required if adjuster should be applied. Defaults to None.
        iter (bool, optional): If the adjuster should be applied in an iterative manner during the iterative applications of the focal operation (iter = True) or afterwards once (iter = False). Defaults to True.
        baseline (bool, optional): Argument onto whether to apply a scaling based on the baseline and traffic coefficients. Defaults to False.
        baseline_coeff (int, optional): a calibrated parameter for scaling the baseline NO2. Defaults to 1.
        traffemissioncoeff_onroad (float): a calibration parameter for scaling the onroad emissions. Defaults to 1.
        traffemissioncoeff_offroad (float): a calibration parameter for scaling the offroad emissions.Defaults to 1.


    Returns:
        array: the flattened  mean estimated NO2 values of the raster after the dispersion of the traffic NO2 values for that month.
    """
    FinalPred = np.zeros(baselineNO2.shape)
    for hour in range(24):
        FinalPred +=  compute_hourly_dispersion(raster = raster, TrafficNO2 = TrafficNO2perhour.iloc[:,hour], baselineNO2 = baselineNO2, onroadindices = onroadindices, 
                                                weightmatrix = weightmatrix, nr_repeats = nr_repeats, adjuster=adjuster, iter = iter, 
                                                           baseline = baseline, baseline_coeff = baseline_coeff, 
                                                          traffemissioncoeff_onroad = traffemissioncoeff_onroad, 
                                                          traffemissioncoeff_offroad = traffemissioncoeff_offroad)
    return FinalPred / 24


def compute_MeteoMatrixsizeRepeats(raster, baselineNO2, TrafficNO2perhour, onroadindices, 
                                   params, matrixsize, meteovalues, observations,
                                   meteolog = False, metric = "R"):
    weightmatrix = returnCorrectWeightedMatrix(meteolog, matrixsize, meteoparams= params[1:], meteovalues = meteovalues)
    Pred = compute_mean_monthly_dispersion(raster = raster, baselineNO2 = baselineNO2, TrafficNO2perhour= TrafficNO2perhour,
                                           onroadindices = onroadindices,weightmatrix = weightmatrix,
                                           nr_repeats=params[0])
    return performance_metrics.compute_Metric(pred=Pred, obs = observations, metric= metric)


def compute_MorphAdjust(raster, baselineNO2, TrafficNO2perhour, onroadindices, 
                meteovalues, observations, meteoparams, adjuster, matrixsize, 
                nr_repeats, meteolog = False, iter = False, metric = "R"):
    weightmatrix = returnCorrectWeightedMatrix(meteolog, matrixsize, meteoparams= meteoparams, meteovalues = meteovalues)
    Pred = compute_mean_monthly_dispersion(raster = raster, baselineNO2 = baselineNO2, TrafficNO2perhour= TrafficNO2perhour,
                                           onroadindices = onroadindices, weightmatrix = weightmatrix, nr_repeats=nr_repeats, adjuster=adjuster, iter = iter)
    return performance_metrics.compute_Metric(pred=Pred, obs = observations, metric= metric)

def compute_MeteoNrRepeats(params, raster, baselineNO2, TrafficNO2perhour, onroadindices, 
                meteovalues, observations, meteoparams, adjuster, matrixsize
                , meteolog = False, iter = False, metric = "R"):
    weightmatrix = returnCorrectWeightedMatrix(meteolog, matrixsize, meteoparams= meteoparams, meteovalues = meteovalues)
    nr_repeats = params[0] + (params[1] * meteovalues[2])
    Pred = compute_mean_monthly_dispersion(raster = raster, baselineNO2 = baselineNO2, TrafficNO2perhour= TrafficNO2perhour,
                                           onroadindices = onroadindices, weightmatrix = weightmatrix, nr_repeats=nr_repeats, adjuster=adjuster, iter = iter)
    return performance_metrics.compute_Metric(pred=Pred, obs = observations, metric= metric)

def compute_Scaling(params, raster, baselineNO2, TrafficNO2perhour, onroadindices, 
                meteovalues, observations, meteoparams, adjuster, matrixsize, repeatsparams,
                meteolog = False, iter = False, metric = "R"):
    weightmatrix = returnCorrectWeightedMatrix(meteolog, matrixsize, meteoparams= meteoparams, meteovalues = meteovalues)
    nr_repeats = repeatsparams[0] + (repeatsparams[1] * meteovalues[2])
    Pred = compute_mean_monthly_dispersion(raster = raster, baselineNO2 = baselineNO2, TrafficNO2perhour= TrafficNO2perhour,
                                           onroadindices = onroadindices, weightmatrix = weightmatrix, 
                                           nr_repeats=nr_repeats, adjuster=adjuster, iter = iter,  baseline = True,
                                           baseline_coeff = params[0], traffemissioncoeff_onroad= params[1],  
                                           traffemissioncoeff_offroad= params[2])
    return performance_metrics.compute_Metric(pred=Pred, obs = observations, metric= metric)



def computehourlymonthlyperformance(raster, TrafficNO2perhour, baselineNO2, onroadindices, 
                                    matrixsize, meteoparams, repeatsparams, meteovalues_df, 
                                    observations, morphparams = None, scalingparams = [1,1,1], 
                                    moderator_df = None, iter = True, baseline = False, meteolog = False):
    """This function computes the performance of the dispersion model using hourly and monthly data depending on the arguments.
    
    Args:
        raster (xarray raster): the raster that is used for the dispersion model (xarray format (see package doc)) .
        TrafficNO2perhour (dataframe(float)): The dataframe with the hourly traffic NO2 values for each raster cell. Only the cells on roads should have values the rest default to 0.
        baselineNO2 (vector(float)): The list of baseline NO2 values for each raster cell.
        onroadindices (list(int)): A list of the indices of the cells that are on roads.
        matrixsize (int): And odd integer that specifies the size of the matrix that is used for the dispersion model.
        meteovalues_df (dataframe(float)): A dataframe of all meteorological values for each month (months are rows). The dataframe should have the columns "Temperature", "Rain", "Windspeed", "Winddirection" in that order.
        observations (dataframe(float)): A dataframe of all cells with observations/measured data for each month and each hour (organised as m0h0, m0h1, m0h3..m1h0..m11h23). This data will be used as ground truth data for performance evaluation.
        meteoparams (list(float)): A list of calibrated meteorological parameters that are used for the weighted matrix.
        repeatsparams (list(float)): A list of calibrated parameters that are used for the number of repeats of the focal operation. This could be a single value or a value that is dependent on the meteorological values.
        morphparams (list(float), optional): A list of calibrated parameters that are used for the morphological adjuster. Defaults to None.
        scalingparams (list(float), optional): A calibrated parameter list for scaling the traffic values and baseline NO2. Defaults to [1,1,1], which means no scaling in effect.
        moderator_df (_type_, optional): Contains the morphological moderator variables that are used for the adjuster. Defaults to None.
        iter (bool, optional): If the adjuster should be applied in an iterative manner during the iterative applications of the focal operation (iter = True) or afterwards once (iter = False). Defaults to True.
        baseline (bool, optional): Argument onto whether to apply a scaling based on the baseline and traffic coefficients. Defaults to False.
        meteolog (Boolean): if True, the log of the meteorological values is taken apart from winddirection. Defaults to False.

    Returns:
        float, float, float, float: R2, RMSE, MAE, ME
    """
    if morphparams is not None:
        adjuster = provide_adjuster( morphparams = morphparams, GreenCover = moderator_df["GreenCover"], openspace_fraction = moderator_df["openspace_fraction"], 
                            NrTrees =  moderator_df["NrTrees"], building_height = moderator_df["building_height"], 
                            neigh_height_diff = moderator_df["neigh_height_diff"])
    else:
        adjuster = None
    rs, MSEs, MAEs, MEs = [], [],  [], []
    for month in range(12):
            weightmatrix = returnCorrectWeightedMatrix(meteolog, matrixsize, meteoparams= meteoparams, meteovalues = meteovalues_df.iloc[month].values)
            if len(repeatsparams) > 1:
                nr_repeats = repeatsparams[0] + (repeatsparams[1] * meteovalues_df.iloc[month, 2])
            else: 
                nr_repeats = int(repeatsparams[0])
            for hour in range(24):
                Pred =  compute_hourly_dispersion(raster = raster, TrafficNO2 = TrafficNO2perhour.iloc[:,hour], baselineNO2 = baselineNO2,
                                                  onroadindices = onroadindices, weightmatrix = weightmatrix, nr_repeats = nr_repeats,
                                                  adjuster=adjuster, iter = iter, baseline = baseline, baseline_coeff = scalingparams[0], 
                                                traffemissioncoeff_onroad = scalingparams[1],traffemissioncoeff_offroad = scalingparams[2])
                r, MSE, MAE, ME = performance_metrics.compute_all_metrics(pred=Pred, obs = observations.iloc[:,(month * 24) + hour])
                rs.append(r)
                MSEs.append(MSE)
                MAEs.append(MAE)
                MEs.append(ME)
    performance_metrics.print_all_metrics(np.mean(rs), np.mean(MSEs), np.mean(MAEs), np.mean(MEs), prefix = "HourlyMonthlyEvaluation")
    return np.mean(rs)**2, sqrt(np.mean(MSEs)), np.mean(MAEs), np.mean(MEs)


def makeR2ErrorRMSEfunctions(computefunction, nr_cpus, data_presets, observations, 
                             meteovalues_df, uniqueparams, adjustercalib = False, 
                             moderator_df = None):
    """This function creates the different performance functions for the calibration of the dispersion model (R2, Errors, RMSE) 
    based on the computefunction and data_presets and uniqueparams. The computefunction is the function that is used to compute the
    dispersion model and the fitness compared to the observed data. The data_presets are the data that is used for the dispersion model. 
    The uniqueparams are the parameters that are unique data or settings for the specific computefunction. 
    The adjustercalib argument specifies whether the adjuster parameters are calibrated or not (It is only used for the morph calibration).
    The moderator_df argument is only used for the morph calibration and contains the moderator variables that are used for the adjuster.

    Args:
        computefunction (function): The function that is used to compute the fitness of the inserted parameters when comparing to observed data.
        nr_cpus (int): The number of threats that should be used for parallelization.
        data_presets (dict(int, raster, df, list, list)): A dictionary of all data that is required for the computefunction. It is computed in the makeFitnessfunction function and contains: "matrixsize", "raster", "TrafficNO2perhour", "baselineNO2", "onroadindices".
        observations (dataframe(float)): A dataframe of all cells with observations/measured data for each month. This data will be used as ground truth data for calibration.
        meteovalues_df (dataframe(float)): A dataframe of all meteorological values for each month (months are rows). The dataframe should have the columns "Temperature", "Rain", "Windspeed", "Winddirection" in that order.
        uniqueparams (dict, optional): A dictionary of all settings and data that are only required for the specific calibtype. Defaults to {}.
        adjustercalib (bool, optional): Specifies whether the adjuster parameters are calibrated or not (True only for calibtype == morph). Defaults to False.
        moderator_df (_type_, optional): Contains the morphological moderator variables that are used for the adjuster. Defaults to None.

    Returns:
        function, function, function: fitnessfunctionR, fitnessfunctionErrors, fitnessfunctionRMSE
    """
    if adjustercalib:
        def fitnessfunctionR(params):
            adjuster = provide_adjuster( morphparams = params, GreenCover = moderator_df["GreenCover"], openspace_fraction = moderator_df["openspace_fraction"], 
                                        NrTrees =  moderator_df["NrTrees"], building_height = moderator_df["building_height"], 
                                        neigh_height_diff = moderator_df["neigh_height_diff"])
            uniqueparams.update({"adjuster": adjuster})
            r = Parallel(n_jobs=nr_cpus)(delayed(computefunction)(**data_presets, meteovalues = meteovalues_df.iloc[month].values, 
                                                                    observations = observations.iloc[:,month],
                                                                    **uniqueparams, metric = "R2"  ) for month in range(12))
            performance_metrics.print_R2(np.mean(r))
            return 1-np.mean(r)
        def fitnessfunctionErrors(params):
            adjuster = provide_adjuster( morphparams = params, GreenCover = moderator_df["GreenCover"], openspace_fraction = moderator_df["openspace_fraction"], 
                                        NrTrees =  moderator_df["NrTrees"], building_height = moderator_df["building_height"], 
                                        neigh_height_diff = moderator_df["neigh_height_diff"])
            uniqueparams.update({"adjuster": adjuster})
            results = Parallel(n_jobs=nr_cpus)(delayed(computefunction)(**data_presets, meteovalues = meteovalues_df.iloc[month].values, 
                                                                    observations = observations.iloc[:,month],
                                                                    **uniqueparams, metric = "Errors") for month in range(12))
            MSE, MAE, ME = zip(*results)
            performance_metrics.print_Errors(np.mean(MSE), np.mean(MAE), np.mean(ME), prefix = "")
            return sqrt(np.mean(MSE)), np.mean(MAE), np.mean(ME)
        def fitnessfunctionRMSE(params):
            adjuster = provide_adjuster( morphparams = params, GreenCover = moderator_df["GreenCover"], openspace_fraction = moderator_df["openspace_fraction"], 
                                        NrTrees =  moderator_df["NrTrees"], building_height = moderator_df["building_height"], 
                                        neigh_height_diff = moderator_df["neigh_height_diff"])
            uniqueparams.update({"adjuster": adjuster})
            MSE = Parallel(n_jobs=nr_cpus)(delayed(computefunction)(**data_presets, meteovalues = meteovalues_df.iloc[month].values, 
                                                                    observations = observations.iloc[:,month],
                                                                    **uniqueparams, metric = "RMSE") for month in range(12))
            performance_metrics.print_RMSE(np.mean(MSE), prefix = "")
            return sqrt(np.mean(MSE))
        return fitnessfunctionR, fitnessfunctionErrors, fitnessfunctionRMSE
    else:
        def fitnessfunctionR(params):
            r = Parallel(n_jobs=nr_cpus)(delayed(computefunction)(**data_presets, params = params,  meteovalues = meteovalues_df.iloc[month].values, 
                                                                    observations = observations.iloc[:,month],
                                                                    **uniqueparams, metric = "R2"  ) for month in range(12))
            performance_metrics.print_R2(np.mean(r))
            return 1-np.mean(r)
        def fitnessfunctionErrors(params):
            results = Parallel(n_jobs=nr_cpus)(delayed(computefunction)( **data_presets, params = params,  meteovalues = meteovalues_df.iloc[month].values, 
                                                                    observations = observations.iloc[:,month],
                                                                    **uniqueparams, metric = "Errors") for month in range(12))
            MSE, MAE, ME = zip(*results)
            performance_metrics.print_Errors(np.mean(MSE), np.mean(MAE), np.mean(ME), prefix = "")
            return sqrt(np.mean(MSE)), np.mean(MAE), np.mean(ME)
        def fitnessfunctionRMSE(params):
            MSE = Parallel(n_jobs=nr_cpus)(delayed(computefunction)( **data_presets, params = params, meteovalues = meteovalues_df.iloc[month].values, 
                                                                    observations = observations.iloc[:,month],
                                                                    **uniqueparams, metric = "RMSE") for month in range(12))
            performance_metrics.print_RMSE(np.mean(MSE), prefix = "")
            return sqrt(np.mean(MSE))
        return fitnessfunctionR, fitnessfunctionErrors, fitnessfunctionRMSE




def makeFitnessfunction(calibtype, nr_cpus, matrixsize, raster, baselineNO2, 
                        TrafficNO2perhour, onroadindices, observations,  meteovalues_df, 
                        metric = "R2", uniqueparams = {},  moderator_df = None):
    """This function creates a fitness function for the calibration of the dispersion model. The fitness function 
    is dependent on the calibration type and the metric. The calibration type can be one of "meteomatrixsizerepeats",
    "morph", "meteonrrepeat". The metric can be one of "R2", "RMSE". The uniqueparams argument should contain the
    parameters that are unique for the calibration type. The moderator_df argument should be provided if the
    calibration type is "morph". The function returns two functions: the fitness function and the other performance
    function. The fitness function is the function that is minimized during calibration and is based on the specified metric.
    The other performance function is the function that is used to evaluate the performance of the model. 
    
    Args:
        calibtype (str): specifies what part of the model should be calibrated. One of "meteomatrixsizerepeats", "morph", "meteonrrepeat".
        nr_cpus (int): The number of threats that should be used for parallelization.
        matrixsize (int): And odd integer that specifies the size of the matrix that is used for the dispersion model.
        raster (xarray raster): the raster that is used for the dispersion model (xarray format (see package doc)) .
        baselineNO2 (vector(float)): The list of baseline NO2 values for each raster cell.
        TrafficNO2perhour (dataframe(float)): The dataframe with the hourly traffic NO2 values for each raster cell. Only the cells on roads should have values the rest default to 0.
        onroadindices (list(int)): A list of the indices of the cells that are on roads.
        observations (dataframe(float)): A dataframe of all cells with observations/measured data for each month. This data will be used as ground truth data for calibration.
        meteovalues_df (dataframe(float)): A dataframe of all meteorological values for each month (months are rows). The dataframe should have the columns "Temperature", "Rain", "Windspeed", "Winddirection" in that order.
        metric (str, optional): One of "R2", "RMSE". Defaults to "R2".
        uniqueparams (dict, optional): A dictionary of all settings and data that are only required for the specific calibtype. Defaults to {}.
        moderator_df (_type_, optional): Contains the morphological moderator variables that are used for the adjuster. Defaults to None.

    Raises:
        ValueError: "uniqueparams must contain meteolog" if calibtype is "meteomatrixsizerepeats" and meteolog is not in uniqueparams
        ValueError: "uniqueparams must contain meteoparams" if calibtype is "morph" and meteoparams is not in uniqueparams
        ValueError: "uniqueparams must contain iter" if calibtype is "morph" and iter is not in uniqueparams
        ValueError: "uniqueparams must contain nr_repeats" if calibtype is "morph" and nr_repeats is not in uniqueparams
        ValueError: "uniqueparams must contain meteolog" if calibtype is "morph" and meteolog is not in uniqueparams
        ValueError: "moderator_df must be provided" if calibtype is "morph" and moderator_df is None
        ValueError: "uniqueparams must contain meteoparams" if calibtype is "meteonrrepeat" and meteoparams is not in uniqueparams
        ValueError: "uniqueparams must contain adjuster" if calibtype is "meteonrrepeat" and adjuster is not in uniqueparams
        ValueError: "uniqueparams must contain iter" if calibtype is "meteonrrepeat" and iter is not in uniqueparams
        ValueError: "uniqueparams must contain meteolog" if calibtype is "meteonrrepeat" and meteolog is not in uniqueparams

    Returns:
        function, function: fitnessfunction, otherperformancefunction
    """
    data_presets = {
        "matrixsize": matrixsize,
        "raster": raster,
        "TrafficNO2perhour": TrafficNO2perhour,
        "baselineNO2": baselineNO2,
        "onroadindices": onroadindices}
        
    if calibtype == "meteomatrixsizerepeats":
        # requires uniqueparams: meteolog
        # test if uniqueparams contains meteolog
        if "meteolog" not in uniqueparams.keys():
            raise ValueError("uniqueparams must contain meteolog") 
        fitnessfunctionR, fitnessfunctionErrors, fitnessfunctionRMSE = makeR2ErrorRMSEfunctions(computefunction = compute_MeteoMatrixsizeRepeats, 
                                                                                                nr_cpus = nr_cpus, data_presets = data_presets, 
                                                                                                observations = observations, meteovalues_df = meteovalues_df,
                                                                                                uniqueparams  = uniqueparams)
    elif calibtype == "morph":
        # requires uniqueparams: meteoparams, iter, nr_repeats, meteolog, 
        if "meteoparams" not in uniqueparams.keys():
            raise ValueError("uniqueparams must contain meteoparams")
        if "iter" not in uniqueparams.keys():
            raise ValueError("uniqueparams must contain iter")
        if "nr_repeats" not in uniqueparams.keys():
            raise ValueError("uniqueparams must contain nr_repeats")
        if "meteolog" not in uniqueparams.keys():
            raise ValueError("uniqueparams must contain meteolog")
        # requires moderator_df
        if moderator_df is None:
            raise ValueError("moderator_df must be provided")
        fitnessfunctionR, fitnessfunctionErrors, fitnessfunctionRMSE = makeR2ErrorRMSEfunctions(computefunction = compute_MorphAdjust, 
                                                                                                nr_cpus = nr_cpus, data_presets = data_presets, 
                                                                                                observations = observations, meteovalues_df = meteovalues_df,
                                                                                                uniqueparams  = uniqueparams, adjustercalib=True, moderator_df=moderator_df)
    elif calibtype == "meteonrrepeat":
        # requires uniqueparams: meteoparams, adjuster, iter, meteolog
        #test if uniqueparams contains meteoparams, adjuster, iter,  meteolog
        if "meteoparams" not in uniqueparams.keys():
            raise ValueError("uniqueparams must contain meteoparams")
        if "adjuster" not in uniqueparams.keys():
            raise ValueError("uniqueparams must contain adjuster")
        if "iter" not in uniqueparams.keys():
            raise ValueError("uniqueparams must contain iter")
        if "meteolog" not in uniqueparams.keys():
            raise ValueError("uniqueparams must contain meteolog")
        fitnessfunctionR, fitnessfunctionErrors, fitnessfunctionRMSE = makeR2ErrorRMSEfunctions(computefunction = compute_MeteoNrRepeats, 
                                                                                                nr_cpus = nr_cpus, data_presets = data_presets, 
                                                                                                observations = observations, meteovalues_df = meteovalues_df,
                                                                                                uniqueparams  = uniqueparams)
    elif calibtype == "scaling":
        if "meteoparams" not in uniqueparams.keys():
            raise ValueError("uniqueparams must contain meteoparams")
        if "adjuster" not in uniqueparams.keys():
            raise ValueError("uniqueparams must contain adjuster")
        if "iter" not in uniqueparams.keys():
            raise ValueError("uniqueparams must contain iter")
        if "meteolog" not in uniqueparams.keys():
            raise ValueError("uniqueparams must contain meteolog")
        if "repeatsparams" not in uniqueparams.keys():
            raise ValueError("uniqueparams must contain repeatsparams")
        fitnessfunctionR, fitnessfunctionErrors, fitnessfunctionRMSE = makeR2ErrorRMSEfunctions(computefunction = compute_Scaling, 
                                                                                                nr_cpus = nr_cpus, data_presets = data_presets, 
                                                                                                observations = observations, meteovalues_df = meteovalues_df,
                                                                                                uniqueparams  = uniqueparams)

    if metric == "R2":
        return fitnessfunctionR, fitnessfunctionErrors
    elif metric == "RMSE":
        return fitnessfunctionRMSE, fitnessfunctionR



def runGAalgorithm(fitnessfunction, param_settings, popsize, max_iter_noimprov, seed = None):
    """This function runs the genetic algorithm for the calibration of the dispersion model. 
    The function returns the genetic algorithm object.

    Args:
        fitnessfunction (function): The fitness function that is used for the calibration.
        param_settings (dataframe[["params_names", "upper", "lower"]]): A dataframe of the parameters that are calibrated. The dataframe should have the columns "param_names", "lower", "upper".
        popsize (int): The population size of the genetic algorithm.
        max_iter_noimprov (int): The maximum number of iterations without improvement of the fitness function.
        seed (int, optional): The seed of the GA for reproducibility. Defaults to None.

    Returns:
        GAobject: Returns the genetic algorithm object that finished calibrating.
    """
    GAalgorithm = ga(function=fitnessfunction,
                dimension=len(param_settings["params_names"]),
                variable_type='real',
                variable_boundaries=  np.column_stack((param_settings['lower'], param_settings['upper'])),
                variable_type_mixed=None,
                function_timeout=1800,  # 30 minutes
                algorithm_parameters={'max_num_iteration': None,
                                    'population_size': popsize,
                                    'mutation_probability': 0.1,
                                    'elit_ratio': 0.01,
                                    'parents_portion':0.3,
                                    'crossover_type': 'uniform',
                                    'max_iteration_without_improv': max_iter_noimprov})
    begin = datetime.now()
    GAalgorithm.run(studEA = True, no_plot = True, seed = seed)
    end = datetime.now()
    print("beginning: ", begin, "end: ", end)
    return GAalgorithm


def AddGAsettingstoDF(param_settings, cellsize, popsize, max_iter_noimprov, seed, calibtype,calibdata, objectivefunction, uniqueparams = {}, matrixsize = None):
    """This function adds the settings of the genetic algorithm to the dataframe with 
    the parameters and parameter bounds that are calibrated.
    
    Args:
        param_settings (dataframe[["params_names", "upper", "lower"]]): A dataframe of the parameters that are calibrated. The dataframe should have the columns "param_names", "lower", "upper".
        cellsize (int): The cellsize of the raster that is used for the dispersion model.
        popsize (int): The population size of the genetic algorithm.
        max_iter_noimprov (int): The maximum number of iterations without improvement of the fitness function.
        seed (int): The seed of the GA for reproducibility.
        calibtype (str): specifies what part of the model should be calibrated. One of "meteomatrixsizerepeats", "morph", "meteonrrepeat".
        calibdata (str): The data that is used for calibration. One of "Palmes", "LML", "RIVM".
        objectivefunction (str): The metric that is used for calibration. One of "R2", "RMSE".
        uniqueparams (dict, optional): any unique parameters to this calibration that should be saved. Defaults to {}.
        matrixsize (int, optional): And odd integer that specifies the size of the matrix that is used for the dispersion model. Defaults to None.
        
    Returns:
        dataframe: The dataframe with the parameters that are calibrated and the settings of the genetic algorithm.
    """
    param_settings = param_settings.copy()
    param_settings['cellsize'] = cellsize
    param_settings['pop_size'] = popsize
    param_settings['max_iter_noimprov'] = max_iter_noimprov
    param_settings['seed'] = seed
    param_settings['calibtype'] = calibtype
    param_settings['calibdata'] = calibdata
    param_settings['objectivefunction'] = objectivefunction
    for el in uniqueparams.keys():
        # if el is a boolean or string
        if type(uniqueparams[el]) == bool or type(uniqueparams[el]) == str:
            param_settings[el] = uniqueparams[el]
    if matrixsize is not None:
        param_settings['matrixsize'] = matrixsize
    return param_settings


def PolishSaveGAresults(GAalgorithm, param_settings, fitnessfunction, otherperformancefunction, suffix):
    """This function polishes the results of the genetic algorithm and saves the results to csv files.
    
    Args:
        GAalgorithm (GAobject): The genetic algorithm object that finished calibrating.
        param_settings (dataframe[["params_names", "upper", "lower"]]): A dataframe of the parameters that are calibrated. The dataframe should at least have the columns "param_names", "lower", "upper".
        fitnessfunction (function): The fitness function that is used for the calibration.
        otherperformancefunction (function): The other performance function that is used for the evaluation.
        suffix (str): A suffix that is added to the filenames of the csv files that are saved.
        
    Returns:
        None
    """
    params_values = GAalgorithm.result["variable"]
    print("best values: ", params_values)
    param_settings = param_settings.copy()
    param_settings['values'] = params_values
    if param_settings["objectivefunction"].iloc[0] == "R2":
        param_settings['R2'] = (1-(fitnessfunction(params_values)))**2
        param_settings['RMSE'], param_settings["MAE"], param_settings["ME"] = otherperformancefunction(params_values)
    elif param_settings["objectivefunction"].iloc[0] == "RMSE":
        param_settings['R2'] = (1-(otherperformancefunction(params_values)))**2
        param_settings['RMSE'] = fitnessfunction(params_values)
    param_settings.to_csv(f"GAparam_results_{suffix}.csv", index=False)
    report = GAalgorithm.report
    pd.DataFrame(report).to_csv(f"GAreport_{suffix}.csv", index=False)
    last_generation = GAalgorithm.result["last_generation"]
    lastGenresults = pd.DataFrame(last_generation["variables"])
    if param_settings["objectivefunction"].iloc[0] == "R2":
        lastGenresults["R2"] = (1-(last_generation["scores"]))**2
    elif param_settings["objectivefunction"].iloc[0] == "RMSE":
        lastGenresults['RMSE'] = last_generation["scores"]
    lastGenresults.to_csv(f"GAlast_generation_{suffix}.csv", index=False)


def addnewoptimalparams(optimalparamdict, calibtype, newoptimalparams, suffix):
    """This function adds the optimal parameters of the genetic algorithm to the optimalparamdict.
    
    Args:
        optimalparamdict (dict): A dictionary of the optimal parameters of the genetic algorithm.
        calibtype (str): specifies what part of the model should be calibrated. One of "meteomatrixsizerepeats", "morph", "meteonrrepeat".
        newoptimalparams (list(float)): The newly calibrated optimal params
        
    Returns:
        dict: The updated dictionary of the optimal parameters of the genetic algorithm.
    """
    if calibtype == "meteomatrixsizerepeats":
        optimalparamdict["meteoparams"] = newoptimalparams[1:]
        optimalparamdict["nr_repeats"] = int(newoptimalparams[0])
    elif calibtype == "morph":
        optimalparamdict["morphparams"] = newoptimalparams
    elif calibtype == "meteonrrepeat":
        optimalparamdict["repeatsparams"] = newoptimalparams
    elif calibtype == "scaling":
        optimalparamdict["scalingparams"] = newoptimalparams
    with open(f'optimalparams_{suffix}.json', 'w') as f:
        json.dump(optimalparamdict, f)
    print("optimal parameters: ", optimalparamdict)

    
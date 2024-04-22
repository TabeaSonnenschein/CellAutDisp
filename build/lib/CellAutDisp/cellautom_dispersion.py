import numpy as np
from xrspatial  import focal
from xrspatial.utils import ngjit
import pandas as pd

def set_onroadvalues(airpollraster, onroadvalues, newvals = None):
    """This function takes a raster and a dataframe with onroadvalues 
    and sets the onroadvalues in the raster to the values in the dataframe.

    Args:
        airpollraster (raster(float)): the raster with the airpollution values
        onroadvalues (df(float, int)): a dataframe with the onroadvalues and the corresponding cell ids

    Returns:
        raster(float): returns the updated raster with the onroadvalues
    """
    if newvals is None:
        newvals = (np.asarray(airpollraster[:]).flatten())
    newvals[onroadvalues["int_id"]] = onroadvalues.iloc[:,1]
    airpollraster[:] = np.array(newvals).reshape(airpollraster.shape)
    return airpollraster

    
def apply_adjuster(airpollraster, adjuster):
    """The function takes the airpollution raster and 
    the adjuster vector and applies the adjuster to the airpollution raster.

    Args:
        airpollraster (raster(float)): the raster with the airpollution values
        adjuster (list(float)): A list of morphological adjustment factors for each cell

    Returns:
        list(float): a list with the adjusted airpollution values
    """
    return (np.asarray(airpollraster[:]).flatten() + (np.asarray(airpollraster[:]).flatten() * adjuster))


def apply_traffemission_coeffs(newvals, onroadvalues, traffemissioncoeff_onroad, traffemissioncoeff_offroad):
    """This function takes the airpollution values, the onroadvalues, and the traffemission coefficients
    and applies the traffemission coefficients to the airpollution values.

    Args:
        newvals (list(float)): a list with the adjusted airpollution values
        onroadvalues (df(float, int)): a dataframe with the onroadvalues and the corresponding cell ids
        traffemissioncoeff_onroad (float): a calibration parameter for scaling the onroad emissions
        traffemissioncoeff_offroad (float): a calibration parameter for scaling the offroad emissions

    Returns:
        list(float): a list with the scaled airpollution values
    """
    newvals[onroadvalues["int_id"]] = newvals[onroadvalues["int_id"]]*traffemissioncoeff_onroad
    newvals[~np.isin(np.arange(len(newvals)), onroadvalues["int_id"])] = newvals[~np.isin(np.arange(len(newvals)), onroadvalues["int_id"])]*traffemissioncoeff_offroad
    return newvals


def create_weightedaverage_function(weightmatrix):
    """This function takes a weightmatrix and returns a function that calculates the weighted average of a kernel.

    Args:
        weightmatrix (matrix(float)): the meteorologically defined weight matrix

    Returns:
        function: a function that calculates the weighted average of a kernel using the weightmatrix
    """
    @ngjit    
    def weightedaverage(kernel_data):
       if np.nansum(weightmatrix) == 0:
           return 0
       else:
           return round((np.nansum(np.multiply(kernel_data, weightmatrix))/np.nansum(weightmatrix)),10)
    return weightedaverage


def cellautom_dispersion_dummy(weightmatrix, airpollraster, nr_repeats, baseline_NO2, onroadvalues):
    """This function takes the weightmatrix, the airpollution raster, 
    the number of iterations,the baseline NO2 values, the onroadvalues 
    and applies the cellular automata dispersion model to the airpollution raster. 
    This is the dummy version (the simplest version). 
    It does not contain morphological adjustment factors nor
    scaling coefficients for the baseline and traffic estimations.
    
    Args:
        weightmatrix (matrix(float)): the meteorologically defined weight matrix
        airpollraster (raster(float)): the raster with the initial traffic induced air pollution values
        nr_repeats (int): the calibrated number of iterations
        baseline_NO2 (list(float)): a list of the baseline NO2 values for each cell
        onroadvalues (df(float, int)): a dataframe with the onroadvalues and the corresponding cell ids

    Returns:
        list(float): a list of the estimations of the airpollution values for each cell
    """  
    weightedaverage = create_weightedaverage_function(weightmatrix)
    for _ in range(int(nr_repeats)):
            airpollraster = set_onroadvalues(airpollraster, onroadvalues)
            airpollraster[:] =  focal.apply(raster = airpollraster, kernel= np.full(weightmatrix.shape, 1), func= weightedaverage)
    return (np.asarray(airpollraster[:]).flatten()) + (baseline_NO2)


def cellautom_dispersion_adjust(weightmatrix, airpollraster, nr_repeats, adjuster, baseline_NO2, onroadvalues):
    """This function takes the weightmatrix, the airpollution raster, 
    the number of iterations, the baseline NO2 values, the onroadvalues, 
    the morphological adjuster vector, and applies the cellular automata 
    dispersion model to the airpollution raster.  In this version the adjuster 
    is applied a single time in the end.

    Args:
        weightmatrix (matrix(float)): the meteorologically defined weight matrix
        airpollraster (raster(float)): the raster with the initial traffic induced air pollution values
        nr_repeats (int): the calibrated number of iterations
        adjuster (list(float)): A list of morphological adjustment factors for each cell
        baseline_NO2 (list(float)): a list of the baseline NO2 values for each cell
        onroadvalues (df(float, int)): a dataframe with the onroadvalues and the corresponding cell ids

    Returns:
        list(float): a list of the estimations of the airpollution values for each cell
    """  
    weightedaverage = create_weightedaverage_function(weightmatrix)
    for i in range(int(nr_repeats)):
            airpollraster = set_onroadvalues(airpollraster, onroadvalues)
            airpollraster[:] =  focal.apply(raster = airpollraster, kernel=np.full(weightmatrix.shape, 1), func= weightedaverage)
    newvals = apply_adjuster(airpollraster, adjuster)
    return newvals + baseline_NO2

def cellautom_dispersion_adjust_iter(weightmatrix, airpollraster, nr_repeats, adjuster, baseline_NO2, onroadvalues):
    """This function takes the weightmatrix, the airpollution raster, 
    the number of iterations, the baseline NO2 values, the onroadvalues, 
    the morphological adjuster vector, and applies the cellular automata 
    dispersion model to the airpollution raster. In this version the adjuster 
    is applied in each iteration.

    Args:
        weightmatrix (matrix(float)): the meteorologically defined weight matrix
        airpollraster (raster(float)): the raster with the initial traffic induced air pollution values
        nr_repeats (int): the calibrated number of iterations
        adjuster (list(float)): A list of morphological adjustment factors for each cell
        baseline_NO2 (list(float)): a list of the baseline NO2 values for each cell
        onroadvalues (df(float, int)): a dataframe with the onroadvalues and the corresponding cell ids

    Returns:
        list(float): a list of the estimations of the airpollution values for each cell
    """  
    weightedaverage = create_weightedaverage_function(weightmatrix)
    newvals = np.asarray(airpollraster[:]).flatten() 
    for _ in range(int(nr_repeats)):
            airpollraster = set_onroadvalues(airpollraster, onroadvalues, newvals = newvals)
            airpollraster[:] =  focal.apply(raster = airpollraster, kernel= np.full(weightmatrix.shape, 1), func= weightedaverage)
            newvals = apply_adjuster(airpollraster, adjuster)
    return newvals + baseline_NO2


def cellautom_dispersion_adjust_scaled(weightmatrix, airpollraster, nr_repeats, adjuster, 
                                       baseline_NO2, onroadvalues, baseline_coeff = 1, 
                                       traffemissioncoeff_onroad = 1, traffemissioncoeff_offroad= 1):
    """This function takes the weightmatrix, the airpollution raster, 
    the number of iterations, the baseline NO2 values, the onroadvalues, 
    the morphological adjuster vector, and the baseline and traffemission coefficients
    and applies the cellular automata dispersion model to the airpollution raster. 
    In this version the adjuster is applied a single time in the end. 
    The baseline and traffemission coefficients are applied in the end to scale the estimations.

    Args:
        weightmatrix (matrix(float)): the meteorologically defined weight matrix
        airpollraster (raster(float)): the raster with the initial traffic induced air pollution values
        nr_repeats (int): the calibrated number of iterations
        adjuster (list(float)): A list of morphological adjustment factors for each cell
        baseline_NO2 (list(float)): a list of the baseline NO2 values for each cell
        onroadvalues (df(float, int)): a dataframe with the onroadvalues and the corresponding cell ids
        baseline_coeff (int, optional): a calibrated parameter for scaling the baseline NO2. Defaults to 1.
        traffemissioncoeff_onroad (float): a calibration parameter for scaling the onroad emissions. Defaults to 1.
        traffemissioncoeff_offroad (float): a calibration parameter for scaling the offroad emissions.Defaults to 1.

    Returns:
        list(float): a list of the estimations of the airpollution values for each cell
    """   
    weightedaverage = create_weightedaverage_function(weightmatrix)
    for _ in range(int(nr_repeats)):
           airpollraster= set_onroadvalues(airpollraster, onroadvalues)
           airpollraster[:] =  focal.apply(raster = airpollraster, kernel= np.full(weightmatrix.shape, 1), func= weightedaverage)
    newvals = apply_adjuster(airpollraster, adjuster)
    newvals = apply_traffemission_coeffs(newvals, onroadvalues, traffemissioncoeff_onroad, traffemissioncoeff_offroad)
    return newvals + (baseline_NO2*baseline_coeff)


def cellautom_dispersion_adjust_iter_scaled(weightmatrix, airpollraster, nr_repeats, adjuster, 
                                            baseline_NO2, onroadvalues, baseline_coeff = 1, 
                                            traffemissioncoeff_onroad = 1, traffemissioncoeff_offroad= 1):
        
    """This function takes the weightmatrix, the airpollution raster, 
    the number of iterations, the baseline NO2 values, the onroadvalues, 
    the morphological adjuster vector, and the baseline and traffemission coefficients
    and applies the cellular automata dispersion model to the airpollution raster. 
    In this version the adjuster is applied in each iteration. 
    The baseline and traffemission coefficients are applied in the end to scale the estimations.

    Args:
        weightmatrix (matrix(float)): the meteorologically defined weight matrix
        airpollraster (raster(float)): the raster with the initial traffic induced air pollution values
        nr_repeats (int): the calibrated number of iterations
        adjuster (list(float)): A list of morphological adjustment factors for each cell
        baseline_NO2 (list(float)): a list of the baseline NO2 values for each cell
        onroadvalues (df(float, int)): a dataframe with the onroadvalues and the corresponding cell ids
        baseline_coeff (int, optional): a calibrated parameter for scaling the baseline NO2. Defaults to 1.
        traffemissioncoeff_onroad (float): a calibration parameter for scaling the onroad emissions. Defaults to 1.
        traffemissioncoeff_offroad (float): a calibration parameter for scaling the offroad emissions.Defaults to 1.

    Returns:
        list(float): a list of the estimations of the airpollution values for each cell
    """  
    weightedaverage = create_weightedaverage_function(weightmatrix)
    newvals = np.asarray(airpollraster[:]).flatten() 
    for _ in range(int(nr_repeats)):
            airpollraster = set_onroadvalues(airpollraster, onroadvalues, newvals = newvals)
            airpollraster[:] =  focal.apply(raster = airpollraster, kernel= np.full(weightmatrix.shape, 1), func= weightedaverage)
            newvals = apply_adjuster(airpollraster, adjuster)
    newvals = apply_traffemission_coeffs(newvals, onroadvalues, traffemissioncoeff_onroad, traffemissioncoeff_offroad)
    return newvals + (baseline_NO2*baseline_coeff)


def compute_hourly_dispersion(raster, TrafficNO2, baselineNO2, onroadindices, weightmatrix, nr_repeats, 
                              adjuster = None, iter = True, baseline = False,  baseline_coeff = 1, 
                              traffemissioncoeff_onroad= 1,  traffemissioncoeff_offroad= 1):
    """Computes the dispersion of the traffic NO2 values for one timestep (e.g. hour). 
    The function uses the correct cellautom_dispersion function from the CA_dispersion module 
    depending on the arguments: adjuster, iter and baseline.

    Args:
        raster (xarray raster): the raster that is used for the dispersion model (xarray format (see package doc)) .
        TrafficNO2 (list(float)): The traffic NO2 values for each raster cell for that hour. Only the cells on roads should have values the rest default to 0.
        baselineNO2 (vector(float)): The list of baseline NO2 values for each raster cell.
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
        array: the flattened estimated NO2 values of the raster after the dispersion of the traffic NO2 values for that hour.
    """
    raster[:] = np.array(TrafficNO2.values).reshape(raster.shape)
    if adjuster is not None:
        if iter:
            if baseline:
                return cellautom_dispersion_adjust_iter_scaled(weightmatrix = weightmatrix, airpollraster = raster, 
                                                                                    nr_repeats=nr_repeats, adjuster = adjuster,  baseline_NO2 = baselineNO2, 
                                                                                    onroadvalues= pd.DataFrame({"int_id": onroadindices, "NO2": TrafficNO2[onroadindices]}),
                                                                                    baseline_coeff = baseline_coeff, traffemissioncoeff_onroad = traffemissioncoeff_onroad,
                                                                                    traffemissioncoeff_offroad = traffemissioncoeff_offroad)
            else:
                return cellautom_dispersion_adjust_iter(weightmatrix = weightmatrix, airpollraster = raster, 
                                                                                    nr_repeats=nr_repeats, adjuster = adjuster,  baseline_NO2 = baselineNO2, 
                                                                                    onroadvalues= pd.DataFrame({"int_id": onroadindices, "NO2": TrafficNO2[onroadindices]}))
        else:
            if baseline:
                return cellautom_dispersion_adjust_scaled(weightmatrix = weightmatrix, airpollraster = raster, 
                                                                                    nr_repeats=nr_repeats, adjuster = adjuster,  baseline_NO2 = baselineNO2, 
                                                                                    onroadvalues= pd.DataFrame({"int_id": onroadindices, "NO2": TrafficNO2[onroadindices]}),
                                                                                    baseline_coeff = baseline_coeff, traffemissioncoeff_onroad = traffemissioncoeff_onroad, 
                                                                                    traffemissioncoeff_offroad = traffemissioncoeff_offroad)
            else:
                return cellautom_dispersion_adjust(weightmatrix = weightmatrix, airpollraster = raster, 
                                                                                    nr_repeats=nr_repeats, adjuster = adjuster,  baseline_NO2 = baselineNO2, 
                                                                                    onroadvalues= pd.DataFrame({"int_id": onroadindices, "NO2": TrafficNO2[onroadindices]}))
    else:
        return cellautom_dispersion_dummy(weightmatrix = weightmatrix, airpollraster = raster, 
                                                                 nr_repeats=nr_repeats, baseline_NO2 = baselineNO2, 
                                                                 onroadvalues= pd.DataFrame({"int_id": onroadindices, "NO2": TrafficNO2[onroadindices]}))


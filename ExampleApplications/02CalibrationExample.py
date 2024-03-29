import CellAutDisp.calibration as cal
from CellAutDisp import provide_adjuster
import os
import pandas as pd
import xarray as xr
import copy
import json

#################################################
## This script is an example of how to use the functions in the CellAutDisp package
## to calibrate the model using parallelized genetic algorithm in a stepwise manner (calibrating and adding model components).
## The calibtype determines the component that is calibrated: meteomatrixsizerepeats, morph, meteonrrepeat, addtempdiff, scaling, allparams
## Further, calibtype can be set to "produceMonthlyHourlyPerformance" for the final model performance evaluation.
##
## Please adjust the following parameters to your specific case:
## - data folder
## - cellsize
## - nr_cpus
## - calibtype
## - names and suffixes of your files
#################################################

# Set the data folder
dataFolder = "C:/Users/Tabea/Documents/CellAutDisp_pckg_data/test_data_CellAutDisp"
os.chdir(dataFolder)

## Set the parameters
cellsize = "50m"  #the matrix cell size
print(cellsize) 
nr_cpus = 14 # number of cores to use for parallel processing
suffix = "TrV_TrI_noTrA"

# calibtype should be one of: meteomatrixsizerepeats, morph, meteonrrepeat, addtempdiff, scaling, allparams, produceMonthlyHourlyPerformance
calibtype = "meteomatrixsizerepeats" 
popsize, max_iter_noimprov, seed = 30, 5, 42 #set low for initial testing
calibdata = "Palmes"
GA = True
meteolog = False
iter = False
print_test = True # if True, the fitness function and other performance functions are tested with a set of parameters (set to optimal ones for 50m from the published paper)


# Read raster data and DataFrames
airpoll_grid_raster = xr.open_dataarray(f"AirPollDeterm_grid_{cellsize}.tif", engine="rasterio")[0] # Read raster data using rasterio
moderator_df = pd.read_csv(f"moderator_{cellsize}.csv")     # Read moderator DataFrame
Eval_df = pd.read_csv(f"Eval_{cellsize}.csv")               # Read Eval DataFrame
Eval_df.drop_duplicates(inplace=True)
Pred_df = pd.read_csv(f"Pred_{cellsize}{suffix}.csv")               # Read Pred DataFrame
Pred_df.fillna(0, inplace=True)
Eval_df["int_id"] = Eval_df["int_id"] -1 # then it works as indices
Pred_df["int_id"] = Pred_df["int_id"] -1 # then it works as indices
Eval_df["baseline_NO2"] = Pred_df["baseline_NO2"]
monthlyWeather2019 = pd.read_csv("monthlyWeather2019TempDiff.csv") # Read monthlyWeather2019 DataFrame

data_presets = {
    "raster": airpoll_grid_raster,
    "TrafficNO2perhour": Pred_df[["NO2_0_1_TraffNoBase", "NO2_1_2_TraffNoBase", "NO2_2_3_TraffNoBase", "NO2_3_4_TraffNoBase", "NO2_4_5_TraffNoBase", "NO2_5_6_TraffNoBase", "NO2_6_7_TraffNoBase", "NO2_7_8_TraffNoBase",
                          "NO2_8_9_TraffNoBase", "NO2_9_10_TraffNoBase", "NO2_10_11_TraffNoBase", "NO2_11_12_TraffNoBase", "NO2_12_13_TraffNoBase", "NO2_13_14_TraffNoBase", "NO2_14_15_TraffNoBase", "NO2_15_16_TraffNoBase",
                          "NO2_16_17_TraffNoBase", "NO2_17_18_TraffNoBase", "NO2_18_19_TraffNoBase", "NO2_19_20_TraffNoBase", "NO2_20_21_TraffNoBase", "NO2_21_22_TraffNoBase",
                          "NO2_22_23_TraffNoBase", "NO2_23_24_TraffNoBase"]],
    "baselineNO2": Pred_df["baseline_NO2"],
    "onroadindices": Pred_df.loc[Pred_df["ON_ROAD"] == 1, "int_id"].values,
    "observations": Eval_df[["palmesNO2_1", "palmesNO2_2", "palmesNO2_3",
              "palmesNO2_4", "palmesNO2_5", "palmesNO2_6", "palmesNO2_7",
              "palmesNO2_8", "palmesNO2_9", "palmesNO2_10", "palmesNO2_11",
              "palmesNO2_12"]],
    "meteovalues_df": monthlyWeather2019[["Temperature", "Rain", "Windspeed", "Winddirection"]]
}
data_presets_RIVM = copy.deepcopy(data_presets)
RIVMhourly = ["MeanNO2_0_1", "MeanNO2_1_2", "MeanNO2_2_3", "MeanNO2_3_4",
              "MeanNO2_4_5", "MeanNO2_5_6", "MeanNO2_6_7", "MeanNO2_7_8",
              "MeanNO2_8_9", "MeanNO2_9_10", "MeanNO2_10_11", "MeanNO2_11_12",
              "MeanNO2_12_13", "MeanNO2_13_14", "MeanNO2_14_15", "MeanNO2_15_16",
              "MeanNO2_16_17", "MeanNO2_17_18", "MeanNO2_18_19",
              "MeanNO2_19_20", "MeanNO2_20_21", "MeanNO2_21_22",
              "MeanNO2_22_23", "MeanNO2_23_24"]
data_presets_RIVM["observations"] = Eval_df[[f"{rivm}_month_{month}"  for month in range(1, 13) for rivm in RIVMhourly]]

if calibtype == "meteomatrixsizerepeats":
    param_settings = cal.generateparambounds(calibtype)
    objectivefunction = "R2"
    uniqueparams = {"meteolog": meteolog}
    matrixsize = 3
    optimalparams = {}
    param_settings = cal.AddGAsettingstoDF(param_settings, cellsize, popsize, max_iter_noimprov, 
                                           seed, calibtype,calibdata, objectivefunction, uniqueparams, 
                                           matrixsize=matrixsize)
    print(param_settings)
    run_nr = calibtype + "" + f"MS{matrixsize}Meteolog{uniqueparams['meteolog']}"
    print(run_nr)
    
    fitnessfunction, otherperformancefunction  = cal.makeFitnessfunction(calibtype = calibtype, nr_cpus = nr_cpus, 
                                            matrixsize = matrixsize, **data_presets, uniqueparams=uniqueparams,
                                            metric = objectivefunction)
    if print_test:
        testparams = [2, 0.409800614, 0.011336538, 0.162193556, -0.096161606, 0.674606756, 0.830105679, 0.304843606,0.077548563,4.926544219]
        fitnessfunction(testparams)
        otherperformancefunction(testparams)
        cal.computehourlymonthlyperformance(meteoparams = testparams[1:], repeatsparams=[testparams[0]], 
                                            **data_presets_RIVM, matrixsize=matrixsize, **uniqueparams)

elif calibtype == "morph":
    param_settings = cal.generateparambounds(calibtype)
    objectivefunction = "R2"
    matrixsize = 3
    with open(f"optimalparams_{cellsize}_meteomatrixsizerepeatsMS{matrixsize}MeteoLog{meteolog}.json", "r") as read_file:
        optimalparams = json.load(read_file)
    uniqueparams = {"meteolog": meteolog,  
                    "nr_repeats": optimalparams["nr_repeats"], 
                    "iter": iter,
                    "meteoparams": optimalparams["meteoparams"]}
    uniqueparamsRIVM = copy.deepcopy(uniqueparams)
    
    param_settings = cal.AddGAsettingstoDF(param_settings, cellsize, popsize, max_iter_noimprov, 
                                           seed, calibtype,calibdata, objectivefunction, uniqueparams, 
                                           matrixsize=matrixsize)
    print(param_settings)
    run_nr = calibtype + "" + f"MS{matrixsize}iter{uniqueparams['iter']}MeteoLog{meteolog}"
    print(run_nr)
    fitnessfunction, otherperformancefunction  = cal.makeFitnessfunction(calibtype = calibtype, nr_cpus = nr_cpus, 
                                            matrixsize = matrixsize, **data_presets, uniqueparams=uniqueparams, moderator_df = moderator_df,
                                            metric = objectivefunction)
    if print_test:
        testparams = [-0.654798184, 0.965573098, 1.818205907, 0.985129934, 0.164442684, -0.175486638, 3.414866835, -0.314854772]
        fitnessfunction(testparams)
        otherperformancefunction(testparams)
        del uniqueparamsRIVM["nr_repeats"]
        uniqueparamsRIVM["repeatsparams"] = [optimalparams["nr_repeats"]]
        cal.computehourlymonthlyperformance(morphparams = testparams,**data_presets_RIVM, matrixsize=matrixsize, 
                                            **uniqueparamsRIVM, moderator_df = moderator_df)

elif calibtype == "meteonrrepeat":
    param_settings = cal.generateparambounds(calibtype)
    objectivefunction = "R2"
    matrixsize = 3
    with open(f"optimalparams_{cellsize}_morphMS{matrixsize}iter{iter}MeteoLog{meteolog}.json", "r") as read_file:
        optimalparams = json.load(read_file)
    adjuster = provide_adjuster( morphparams = optimalparams["morphparams"], GreenCover = moderator_df["GreenCover"],
                                openspace_fraction = moderator_df["openspace_fraction"], NrTrees = moderator_df["NrTrees"],
                                building_height = moderator_df["building_height"], neigh_height_diff = moderator_df["neigh_height_diff"])
    uniqueparams = {"meteolog": meteolog,  
                    "adjuster": adjuster, 
                    "iter": iter,
                    "meteoparams": optimalparams["meteoparams"]}
    param_settings = cal.AddGAsettingstoDF(param_settings, cellsize, popsize, max_iter_noimprov, 
                                           seed, calibtype,calibdata, objectivefunction, uniqueparams, 
                                           matrixsize=matrixsize)
    print(param_settings)
    run_nr = calibtype + "" + f"MS{matrixsize}iter{uniqueparams['iter']}MeteoLog{uniqueparams['meteolog']}"
    print(run_nr)
    
    fitnessfunction, otherperformancefunction  = cal.makeFitnessfunction(calibtype = calibtype, nr_cpus = nr_cpus, 
                                            matrixsize = matrixsize, **data_presets, uniqueparams=uniqueparams, moderator_df = moderator_df,
                                            metric = objectivefunction)
    if print_test:
        testparams = [1.734685659, 0.416988784]
        fitnessfunction(testparams)
        otherperformancefunction(testparams)
        uniqueparamsRIVM = copy.deepcopy(uniqueparams)
        del uniqueparamsRIVM["adjuster"]
        uniqueparamsRIVM["repeatsparams"] = testparams
        uniqueparamsRIVM["morphparams"] = optimalparams["morphparams"]
        cal.computehourlymonthlyperformance(**data_presets_RIVM, matrixsize=matrixsize, 
                                            **uniqueparamsRIVM, moderator_df = moderator_df)

elif calibtype == "addtempdiff":
    param_settings = cal.generateparambounds(calibtype)
    objectivefunction = "R2"
    matrixsize = 3
    with open(f"optimalparams_{cellsize}_morphMS{matrixsize}iter{iter}MeteoLog{meteolog}.json", "r") as read_file:
        optimalparams = json.load(read_file)
    adjuster = provide_adjuster( morphparams = optimalparams["morphparams"], GreenCover = moderator_df["GreenCover"],
                                openspace_fraction = moderator_df["openspace_fraction"], NrTrees = moderator_df["NrTrees"],
                                building_height = moderator_df["building_height"], neigh_height_diff = moderator_df["neigh_height_diff"])
    data_presets["meteovalues_df"] = monthlyWeather2019[["Windspeed", "Winddirection","Temperature", "Rain", "TempDifference"]]
    optimalparams["meteoparams"] = [optimalparams["meteoparams"][i] for i in [0,3,4,5,6,7,8,1,2]]
    uniqueparams = {"meteolog": meteolog,  
                    "adjuster": adjuster, 
                    "iter": iter,
                    "nr_repeats": optimalparams["nr_repeats"],
                    "meteoparams": optimalparams["meteoparams"]}
    param_settings = cal.AddGAsettingstoDF(param_settings, cellsize, popsize, max_iter_noimprov, 
                                           seed, calibtype,calibdata, objectivefunction, uniqueparams, 
                                           matrixsize=matrixsize)
    print(param_settings)
    run_nr = calibtype + "" + f"MS{matrixsize}iter{uniqueparams['iter']}MeteoLog{uniqueparams['meteolog']}"
    print(run_nr)
    fitnessfunction, otherperformancefunction  = cal.makeFitnessfunction(calibtype = calibtype, nr_cpus = nr_cpus, 
                                            matrixsize = matrixsize, **data_presets, uniqueparams=uniqueparams, moderator_df = moderator_df,
                                            metric = objectivefunction)
    if print_test:
        testparams = [0]
        fitnessfunction(testparams)
        otherperformancefunction(testparams)
        uniqueparamsRIVM = copy.deepcopy(uniqueparams)
        del uniqueparamsRIVM["adjuster"]
        uniqueparamsRIVM["morphparams"] = optimalparams["morphparams"]
        cal.computehourlymonthlyperformance(**data_presets_RIVM, matrixsize=matrixsize, 
                                            **uniqueparamsRIVM, moderator_df = moderator_df)
    
elif calibtype == "scaling":
    param_settings = cal.generateparambounds(calibtype)
    objectivefunction = "R2"
    matrixsize = 3
    with open(f"optimalparams_{cellsize}_meteonrrepeatMS{matrixsize}iter{iter}MeteoLog{meteolog}.json", "r") as read_file:
        optimalparams = json.load(read_file)
    adjuster = provide_adjuster( morphparams = optimalparams["morphparams"], GreenCover = moderator_df["GreenCover"],
                                openspace_fraction = moderator_df["openspace_fraction"], NrTrees = moderator_df["NrTrees"],
                                building_height = moderator_df["building_height"], neigh_height_diff = moderator_df["neigh_height_diff"])
    uniqueparams = {"meteolog": meteolog,  
                    "adjuster": adjuster, 
                    "iter": iter,
                    "meteoparams": optimalparams["meteoparams"],
                    "repeatsparams": optimalparams["repeatsparams"]}
    param_settings = cal.AddGAsettingstoDF(param_settings, cellsize, popsize, max_iter_noimprov, 
                                           seed, calibtype,calibdata, objectivefunction, uniqueparams, 
                                           matrixsize=matrixsize)
    print(param_settings)
    run_nr = calibtype + "" + f"MS{matrixsize}iter{uniqueparams['iter']}MeteoLog{uniqueparams['meteolog']}"
    print(run_nr)
    fitnessfunction, otherperformancefunction  = cal.makeFitnessfunction(calibtype = calibtype, nr_cpus = nr_cpus, 
                                            matrixsize = matrixsize, **data_presets, uniqueparams=uniqueparams, moderator_df = moderator_df,
                                            metric = objectivefunction)
    Rfunction, Errorsfunction  = cal.makeFitnessfunction(calibtype = calibtype, nr_cpus = nr_cpus, 
                                            matrixsize = matrixsize, **data_presets, uniqueparams=uniqueparams, moderator_df = moderator_df,
                                            metric = "R2")
    
    if print_test: 
        optimalparams50m = [1.9983891,0.690864474,0.760965621]
        fitnessfunction(optimalparams50m)
        otherperformancefunction(optimalparams50m)
        Errorsfunction(optimalparams50m)
        uniqueparamsRIVM = copy.deepcopy(uniqueparams)
        del uniqueparamsRIVM["adjuster"]
        uniqueparamsRIVM["morphparams"] = optimalparams["morphparams"]
        cal.computehourlymonthlyperformance(scalingparams=optimalparams50m, baseline= True, **data_presets_RIVM, matrixsize=matrixsize, 
                                            **uniqueparamsRIVM, moderator_df = moderator_df)

if calibtype == "allparams":
    param_settings = cal.generateparambounds(calibtype)
    objectivefunction = "R2"
    matrixsize = 3
    with open(f"optimalparams_{cellsize}_scalingMS{matrixsize}iter{iter}MeteoLog{meteolog}.json", "r") as read_file:
        optimalparams = json.load(read_file)
    optimalparamslist = optimalparams["meteoparams"]  + optimalparams["morphparams"] + optimalparams["repeatsparams"]+ optimalparams["scalingparams"]
    param_settings["upper"] = [item+abs(item*0.25) for item in optimalparamslist]
    param_settings["lower"] = [item-abs(item*0.25) for item in optimalparamslist]
    
    uniqueparams = {"meteolog": meteolog,  
                    "iter": iter}
    param_settings = cal.AddGAsettingstoDF(param_settings, cellsize, popsize, max_iter_noimprov, 
                                           seed, calibtype,calibdata, objectivefunction, uniqueparams, 
                                           matrixsize=matrixsize)
    print(param_settings)
    run_nr = calibtype + "" + f"MS{matrixsize}iter{uniqueparams['iter']}MeteoLog{uniqueparams['meteolog']}"
    print(run_nr)
    fitnessfunction, otherperformancefunction  = cal.makeFitnessfunction(calibtype = calibtype, nr_cpus = nr_cpus, 
                                            matrixsize = matrixsize, **data_presets, uniqueparams=uniqueparams, moderator_df = moderator_df,
                                            metric = objectivefunction)
    if print_test: 
        fitnessfunction(optimalparamslist)
        # otherperformancefunction(optimalparamslist)
        cal.computehourlymonthlyperformance(morphparams=optimalparamslist[9:17],
                                            meteoparams=optimalparamslist[0:9], 
                                            repeatsparams=optimalparamslist[17:19],
                                            scalingparams=optimalparamslist[19:], 
                                            baseline= True, **data_presets_RIVM, matrixsize=matrixsize, 
                                            moderator_df = moderator_df, meteolog=meteolog, iter=iter)

if calibtype == "produceMonthlyHourlyPerformance":
    matrixsize = 3
    with open(f"optimalparams_{cellsize}_scalingMS{matrixsize}iter{iter}MeteoLog{meteolog}.json", "r") as read_file:
        optimalparams = json.load(read_file)
    del optimalparams["nr_repeats"]
    cal.computehourlymonthlyperformance(baseline= True, **data_presets_RIVM, iter=iter, meteolog=meteolog,
                                        **optimalparams, moderator_df = moderator_df, 
                                        saveHourlyMonthly=True, prefix= "RIVM"+cellsize)
    cal.computemonthlyperformance(baseline= True, **data_presets,  iter=iter, meteolog=meteolog,
                                **optimalparams, moderator_df = moderator_df, 
                                 saveMonthly=True, prefix= "Palmes"+cellsize)
    GA = False
    

if GA:
    GAalgorithm = cal.runGAalgorithm(fitnessfunction, param_settings, popsize, max_iter_noimprov)
    cal.PolishSaveGAresults(GAalgorithm, param_settings, fitnessfunction, otherperformancefunction, 
                            suffix = f"_{cellsize}_{suffix}_{run_nr}_{calibdata}_{objectivefunction}")
    print(GAalgorithm.result["variable"])
    print(list(GAalgorithm.result["variable"]))
    cal.addnewoptimalparams(optimalparamdict = optimalparams, calibtype = calibtype, 
                            newoptimalparams = list(GAalgorithm.result["variable"]), suffix = cellsize +"_"+ run_nr)
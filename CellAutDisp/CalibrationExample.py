import Calibration as cal
import os
import pandas as pd
import xarray as xr
from joblib import Parallel, delayed

# Set the data folder and cell size
dataFolder = "D:/PhD EXPANSE/Data/Amsterdam"
os.chdir(os.path.join(dataFolder, "Air Pollution Determinants"))
cellsize = "25m"
nr_cpus = 15
suffix = "TrV_TrI_noTrA2"

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
monthlyWeather2019 = pd.read_csv(os.path.join(dataFolder, "Weather", "monthlyWeather2019TempDiff.csv")) # Read monthlyWeather2019 DataFrame

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
    "meteovalues_df": monthlyWeather2019[["Temperature", "Rain", "Windspeed", "Winddirection"]],
}

calibtype = "meteomatrixsizerepeats"
popsize, max_iter_noimprov, seed = 10, 2, 42
calibdata = "Palmes"

if calibtype == "meteomatrixsizerepeats":
    params_names = ["nr_repeats","BaseW_intercept","temp_coeff",  "rain_coeff", "windsp_coeff",
                    "dispar_intercept","windsp_disp_coeff", "dist_coeff", "align_coeff", "inertia"]
    param_settings = pd.DataFrame(params_names).rename(columns={0: "params_names"})
    param_settings["lower"] = [2, 0, -1, -1, -1, 0, 0, 0, 0, 0]
    param_settings["upper"] = [15, 1,  2,  2,  2, 3, 2, 2, 2, 9]
    objectivefunction = "R2"
    uniqueparams = {"meteolog": False}
    matrixsize = 3
    param_settings = cal.AddGAsettingstoDF(param_settings, cellsize, popsize, max_iter_noimprov, 
                                           seed, calibtype,calibdata, objectivefunction, uniqueparams, 
                                           matrixsize=matrixsize)
    print(param_settings)
    run_nr = calibtype + "" + f"MS{matrixsize}"
    print(run_nr)
    
    fitnessfunction, otherperformancefunction  = cal.makeFitnessfunction(calibtype = calibtype, nr_cpus = nr_cpus, 
                                            matrixsize = matrixsize, **data_presets, uniqueparams=uniqueparams,
                                            metric = objectivefunction)

    print(fitnessfunction(param_settings["upper"].values))
    GA = True

elif calibtype == "morph":
    params_names = ["Mod_Intercept", "Green_mod", "OpenSp_mod", "Tree_mod", "BuildH_mod", "NeighBuildH_mod"]
    param_settings = pd.DataFrame(params_names).rename(columns={0: "params_names"})
    param_settings["lower"] = [-2, -1, -5, -1, -1, -1]
    param_settings["upper"] = [2,  1,  2,  1,  1,  1]
    objectivefunction = "R2"
    
    meteoparams = []
    uniqueparams = {"meteolog": False,  
                    "nr_repeats": 5, 
                    "iter": False,
                    "meteoparams": meteoparams}

    param_settings = cal.AddGAsettingstoDF(param_settings, popsize, max_iter_noimprov, seed, calibtype,
                                           calibdata, objectivefunction, uniqueparams)
    print(param_settings)
    matrixsize = 3
    run_nr = calibtype + "" + f"MS{matrixsize}"
    print(run_nr)

    fitnessfunction, otherperformancefunction  = cal.makeFitnessfunction(calibtype = calibtype, nr_cpus = nr_cpus, 
                                            matrixsize = matrixsize, **data_presets, uniqueparams=uniqueparams, moderator_df = moderator_df,
                                            metric = objectivefunction)
    GA = True
    
if GA == True:
    GAalgorithm = cal.runGAalgorithm(fitnessfunction, param_settings, popsize, max_iter_noimprov)
    cal.PolishSaveGAresults(GAalgorithm, param_settings, fitnessfunction, otherperformancefunction, 
                            suffix = f"_{cellsize}_{suffix}_{run_nr}_{calibdata}_{objectivefunction}")   
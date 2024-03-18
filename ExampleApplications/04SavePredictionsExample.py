
# Set the data folder and cell size
import os
import pandas as pd
import xarray as xr
import json
from CellAutDisp import saveMonthlyHourlyPredictions, saveTrafficScenarioPredictions, measureMonthlyHourlyComputationTime

##########################################################################################
### This script is an example of how to use the functions in the CellAutDisp package
### to save the predictions for the monthly and hourly NO2 concentrations, the computation time,
### as well as the traffic scenario predictions.
##########################################################################################

## set directory
dataFolder = "C:/Users/Tabea/Documents/CellAutDisp_pckg_data/test_data_CellAutDisp"
os.chdir(dataFolder)

## Set the parameters
cellsize = "50m"
suffix = "TrV_TrI_noTrA"
calibdata = "Palmes"
GA = True
meteolog = False
iter = False
matrixsize = 3
with open(f"optimalparams_{cellsize}_scalingMS{matrixsize}iter{iter}MeteoLog{meteolog}.json", "r") as read_file:
        optimalparams = json.load(read_file)
del optimalparams["nr_repeats"]

# Read raster data and DataFrames
airpoll_grid_raster = xr.open_dataarray(f"AirPollDeterm_grid_{cellsize}.tif", engine="rasterio")[0] # Read raster data using rasterio
moderator_df = pd.read_csv(f"moderator_{cellsize}.csv")     # Read moderator DataFrame
monthlyWeather2019 = pd.read_csv("monthlyWeather2019TempDiff.csv") # Read monthlyWeather2019 DataFrame
Pred_df = pd.read_csv(f"Pred_{cellsize}{suffix}.csv")               # Read Pred DataFrame
Pred_df.fillna(0, inplace=True)

data_presets = {
    "raster": airpoll_grid_raster,
    "TrafficNO2perhour": Pred_df[["NO2_0_1_TraffNoBase", "NO2_1_2_TraffNoBase", "NO2_2_3_TraffNoBase", "NO2_3_4_TraffNoBase", "NO2_4_5_TraffNoBase", "NO2_5_6_TraffNoBase", "NO2_6_7_TraffNoBase", "NO2_7_8_TraffNoBase",
                          "NO2_8_9_TraffNoBase", "NO2_9_10_TraffNoBase", "NO2_10_11_TraffNoBase", "NO2_11_12_TraffNoBase", "NO2_12_13_TraffNoBase", "NO2_13_14_TraffNoBase", "NO2_14_15_TraffNoBase", "NO2_15_16_TraffNoBase",
                          "NO2_16_17_TraffNoBase", "NO2_17_18_TraffNoBase", "NO2_18_19_TraffNoBase", "NO2_19_20_TraffNoBase", "NO2_20_21_TraffNoBase", "NO2_21_22_TraffNoBase",
                          "NO2_22_23_TraffNoBase", "NO2_23_24_TraffNoBase"]],
    "baselineNO2": Pred_df["baseline_NO2"],
    "onroadindices": Pred_df.loc[Pred_df["ON_ROAD"] == 1].index.to_list(),
    "meteovalues_df": monthlyWeather2019[["Temperature", "Rain", "Windspeed", "Winddirection"]],
    "moderator_df": moderator_df
}

saveMonthlyHourlyPredictions(**data_presets, **optimalparams, iter = iter, 
                               baseline = True, meteolog = meteolog, suffix= cellsize)

Scenarios = [0, 0.5, 1, 1.5, 2, 2.5, 3]
saveTrafficScenarioPredictions( trafficfactors = Scenarios, **data_presets, 
                               **optimalparams, iter = iter, baseline = True, 
                                meteolog = meteolog, suffix= cellsize, 
                                cellsubgroups = Pred_df[["int_id", "ON_ROAD", "ROAD_NEIGHBOR"]])

measureMonthlyHourlyComputationTime(**data_presets, **optimalparams, iter = iter, 
                               baseline = True, meteolog = meteolog, suffix= cellsize)
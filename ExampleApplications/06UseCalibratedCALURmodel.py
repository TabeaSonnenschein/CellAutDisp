import os
import pandas as pd
import xarray as xr
import json
from CellAutDisp import returnCorrectWeightedMatrix, provide_adjuster, provide_meteorepeats, compute_hourly_dispersion

##########################################################################################
### This script is an example of how to use the functions in the CellAutDisp package, and the calibrated parameters
### to integrate the CA-LUR model into another other simulation to for example 
### calculate the hourly dispersion of NO2 concentrations.
##########################################################################################


# Set the data folder
dataFolder = "C:/Users/Tabea/Documents/CellAutDisp_pckg_data/test_data_CellAutDisp"
os.chdir(dataFolder)

## Set the parameters
cellsize = "50m"
suffix = "TrV_TrI_noTrA"
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
    "baselineNO2": Pred_df["baseline_NO2"],
    "onroadindices": Pred_df.loc[Pred_df["ON_ROAD"] == 1].index.to_list()
}
param_presets = {
    "iter": iter, 
    "baseline": True,
    "baseline_coeff": optimalparams["scalingparams"][0], 
    "traffemissioncoeff_onroad": optimalparams["scalingparams"][1],
    "traffemissioncoeff_offroad": optimalparams["scalingparams"][2]
}

# adjuster is a static variable
adjuster = provide_adjuster( morphparams = optimalparams["morphparams"], GreenCover = moderator_df["GreenCover"], openspace_fraction = moderator_df["openspace_fraction"], 
                            NrTrees =  moderator_df["NrTrees"], building_height = moderator_df["building_height"], 
                            neigh_height_diff = moderator_df["neigh_height_diff"])

# weightmatrix and nr_repeats are dynamic variables that change with the weather (in our case monthly)
current_weather = list(monthlyWeather2019[["Temperature", "Rain", "Windspeed", "Winddirection"]].iloc[0])

weightmatrix = returnCorrectWeightedMatrix(meteolog, matrixsize, meteoparams= optimalparams["meteoparams"], meteovalues = current_weather)
nr_repeats = provide_meteorepeats(optimalparams["repeatsparams"], current_weather[2])

# the most dynamic variable is the traffic NO2
currentTrafficNO2 = Pred_df["NO2_0_1_TraffNoBase"]

FinalNO2 = compute_hourly_dispersion(**data_presets, weightmatrix = weightmatrix,
                          adjuster = adjuster, TrafficNO2 = currentTrafficNO2,  
                          nr_repeats = nr_repeats, **param_presets)

print(FinalNO2.head(20))

# you can integrate the function and data in a loop or simulation model 
# to calculate the dispersion for each hour and month
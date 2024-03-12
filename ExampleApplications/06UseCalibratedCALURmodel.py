import os
import pandas as pd
import xarray as xr
import json
from CellAutDisp import returnCorrectWeightedMatrix, provide_adjuster, compute_hourly_dispersion

dataFolder = "D:/PhD EXPANSE/Data/Amsterdam"
os.chdir(os.path.join(dataFolder, "Air Pollution Determinants"))

## Set the parameters
cellsize = "25m"
suffix = "TrV_TrI_noTrA2"
calibdata = "Palmes"
GA = True
if cellsize == "50m":
    meteolog = False
else:
    meteolog = True
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

current_weather = monthlyWeather2019[["Temperature", "Rain", "Windspeed", "Winddirection"]].iloc[0]
currentTrafficNO2 = Pred_df["NO2_0_1_TraffNoBase"]

weightmatrix = returnCorrectWeightedMatrix(meteolog, matrixsize, meteoparams= optimalparams["meteoparams"], meteovalues = current_weather)
adjuster = provide_adjuster( morphparams = optimalparams["morphparams"], GreenCover = moderator_df["GreenCover"], openspace_fraction = moderator_df["openspace_fraction"], 
                            NrTrees =  moderator_df["NrTrees"], building_height = moderator_df["building_height"], 
                            neigh_height_diff = moderator_df["neigh_height_diff"])

FinalNO2 = compute_hourly_dispersion(**data_presets, weightmatrix = weightmatrix,
                          adjuster = adjuster, iter= iter, baseline = True,
                          TrafficNO2 = currentTrafficNO2,  nr_repeats, 
                          baseline_coeff = optimalparams["scalingparams"][0], 
                          traffemissioncoeff_onroad= optimalparams["scalingparams"][1],
                          traffemissioncoeff_offroad= optimalparams["scalingparams"][2])

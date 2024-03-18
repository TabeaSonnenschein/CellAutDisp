import xarray as xr
from xrspatial  import focal
from xrspatial.utils import ngjit
import numpy as np
import os
import pandas as pd
import geopandas as gpd
from CellAutDisp import FindRoadNeighboringCells, create_traffic_emission_columns, create_Eval_df

# Set the data folder and cell size
dataFolder = "D:/PhD EXPANSE/Data/Amsterdam"
os.chdir(os.path.join(dataFolder, "Air Pollution Determinants"))
cellsize = "50m"
suffix = "TrV_TrI_noTrA"

# Read raster data and DataFrames
# AirPollGrid = gpd.read_file(f"AirPollDeterm_grid{cellsize}.shp")
# PalmesData = gpd.read_file(dataFolder + "/Air Pollution Determinants/PalmesOffRoadMeasurements/Palmesdata2019gridjoin.shp")
# PalmesID = "Code"
# PalmesCols = ["Janry","Fbrry","March","April","May","June","July","Augst","Sptmb","Octbr","Nvmbr","Dcmbr"]
# Palmesdesiredcols =["palmesNO2_1","palmesNO2_2","palmesNO2_3", 
#                "palmesNO2_4","palmesNO2_5","palmesNO2_6","palmesNO2_7",
#                "palmesNO2_8","palmesNO2_9","palmesNO2_10", "palmesNO2_11",
#                "palmesNO2_12"]
# RMSData = gpd.read_file(dataFolder + "/Air Pollution Determinants/RIVMhourlyOffRoadData/RIVMmonthlyhourly.shp")
# RMSID = "SttnC"
# RMShourly = ["MeanNO2_0_1","MeanNO2_1_2","MeanNO2_2_3","MeanNO2_3_4", 
#                           "MeanNO2_4_5","MeanNO2_5_6","MeanNO2_6_7","MeanNO2_7_8",
#                           "MeanNO2_8_9","MeanNO2_9_10","MeanNO2_10_11", "MeanNO2_11_12",
#                           "MeanNO2_12_13","MeanNO2_13_14", "MeanNO2_14_15", "MeanNO2_15_16",
#                           "MeanNO2_16_17","MeanNO2_17_18", "MeanNO2_18_19", 
#                           "MeanNO2_19_20","MeanNO2_20_21","MeanNO2_21_22", 
#                           "MeanNO2_22_23", "MeanNO2_23_24"]
# RMSmonthly = [f"{rivm}_month_{month}"  for month in range(1, 13) for rivm in RMShourly]
# print(RMSData.columns)
# RMSData.columns = list(RMSData.columns[:4]) + RMSmonthly + ["geometry"]


# Eval_df_Palmes = create_Eval_df(grid_sp = AirPollGrid,
#                gridID = "int_id", 
#                point_observations = PalmesData, 
#                observationsID = PalmesID, 
#                observations_colnames = PalmesCols, 
#                desired_observation_colnames = Palmesdesiredcols, suffix="Palmes")

# Eval_df_RMS = create_Eval_df(grid_sp = AirPollGrid,
#                 gridID = "int_id", 
#                 point_observations = RMSData, 
#                 observationsID = RMSID, 
#                 observations_colnames = RMSmonthly, 
#                 desired_observation_colnames = RMSmonthly, suffix="RMS")

# # merge the two dataframes
# Eval_df = Eval_df_Palmes.merge(Eval_df_RMS, on="int_id", how="inner")
# Eval_df.to_csv(f"Eval_{cellsize}.csv", index=False)


### make Pred_df
# read csv
grid_dataframe = pd.read_csv(f"AirPollDeterm_grid{cellsize}_Predictors_full.csv")
# this dataframe has all predictor variables aggregated to the grid level, including the land use predictors and traffic volume and intensity
# the traffic volume and intensity are in the columns "TrV0_1","TrV1_2",.. and "TrI0_1","TrI1_2", ... respectively

# create columns for NO2 with TrafficVolume and Traffic Intensity without transport area
if cellsize == "50m":
    grid_dataframe["baseline_NO2"] = (1.902e+01 + (grid_dataframe["INDUS_5000"] * 1.939e-07)
                                    + (grid_dataframe["WATER_1000"] * 7.695e-08) + (grid_dataframe["AGRI_5000"] * -2.195e-07)
                                    + (grid_dataframe["PORT_5000"] * 1.531e-07) + (grid_dataframe["NATUR_5000"] * 6.079e-07)
                                    + (grid_dataframe["INDUS_100"] * 6.005e-05) + (grid_dataframe["GreenCover100"] * -6.919e-01))
    grid_dataframe.loc[grid_dataframe["baseline_NO2"] < 0, "baseline_NO2"] = 0
    grid_dataframe = create_traffic_emission_columns(df = grid_dataframe, id = "int_id", TrV_coeff =  2.845e-02 , TrI_coeff = 1.072e-04, suffix="TrV_TrI_noTrAxxx")

elif cellsize == "25m":
    grid_dataframe["baseline_NO2"] = (-5.440e+00 + (grid_dataframe["POP_5000"] * 5.358e-06) +
                                    (grid_dataframe["INDUS_5000"] * 5.499e-07) + (grid_dataframe["NATUR_5000"] * 1.150e-06) +
                                    (grid_dataframe["AGRI_5000"] * 1.170e-07) + (grid_dataframe["PORT_5000"] * 2.297e-07) +
                                    (grid_dataframe["RES_5000"] * 1.823e-07))
    grid_dataframe.loc[grid_dataframe["baseline_NO2"] < 0, "baseline_NO2"] = 0
    grid_dataframe = create_traffic_emission_columns(df = grid_dataframe, id = "int_id", TrV_coeff = 1.586e-02 , TrI_coeff = 1.306e-04, suffix="TrV_TrI_noTrAxxx")
    

# Pred_df = pd.read_csv(f"Pred_{cellsize}{suffix}.csv")               # Read Pred DataFrame
# airpoll_grid_raster = xr.open_dataarray(f"AirPollDeterm_grid_{cellsize}.tif", engine="rasterio")[0] # Read raster data using rasterio
# onroadindices =  Pred_df.loc[Pred_df["ON_ROAD"] == 1, "int_id"].values
# onroadindices = onroadindices-1

# Pred_df["ROAD_NEIGHBOR"] = FindRoadNeighboringCells(airpoll_grid_raster, onroadindices)
# print(Pred_df.head(20))
# Pred_df.to_csv(f"Pred_{cellsize}{suffix}.csv", index=False)
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
AirPollGrid = gpd.read_file(f"AirPollDeterm_grid{cellsize}.shp")
PalmesData = gpd.read_file(dataFolder + "/Air Pollution Determinants/PalmesOffRoadMeasurements/Palmesdata2019gridjoin.shp")
PalmesID = "Code"
PalmesCols = ["Janry","Fbrry","March","April","May","June","July","Augst","Sptmb","Octbr","Nvmbr","Dcmbr"]
Palmesdesiredcols =["palmesNO2_1","palmesNO2_2","palmesNO2_3", 
               "palmesNO2_4","palmesNO2_5","palmesNO2_6","palmesNO2_7",
               "palmesNO2_8","palmesNO2_9","palmesNO2_10", "palmesNO2_11",
               "palmesNO2_12"]
RMSData = gpd.read_file(dataFolder + "/Air Pollution Determinants/RIVMhourlyOffRoadData/RIVMmonthlyhourly.shp")
RMSID = "SttnC"
RMShourly = ["MeanNO2_0_1","MeanNO2_1_2","MeanNO2_2_3","MeanNO2_3_4", 
                          "MeanNO2_4_5","MeanNO2_5_6","MeanNO2_6_7","MeanNO2_7_8",
                          "MeanNO2_8_9","MeanNO2_9_10","MeanNO2_10_11", "MeanNO2_11_12",
                          "MeanNO2_12_13","MeanNO2_13_14", "MeanNO2_14_15", "MeanNO2_15_16",
                          "MeanNO2_16_17","MeanNO2_17_18", "MeanNO2_18_19", 
                          "MeanNO2_19_20","MeanNO2_20_21","MeanNO2_21_22", 
                          "MeanNO2_22_23", "MeanNO2_23_24"]
RMSmonthly = [f"{rivm}_month_{month}"  for month in range(1, 13) for rivm in RMShourly]
print(RMSData.columns)
RMSData.columns = list(RMSData.columns[:4]) + RMSmonthly + ["geometry"]


Eval_df_Palmes = create_Eval_df(grid_sp = AirPollGrid,
               gridID = "int_id", 
               point_observations = PalmesData, 
               observationsID = PalmesID, 
               observations_colnames = PalmesCols, 
               desired_observation_colnames = Palmesdesiredcols, suffix="Palmes")

Eval_df_RMS = create_Eval_df(grid_sp = AirPollGrid,
                gridID = "int_id", 
                point_observations = RMSData, 
                observationsID = RMSID, 
                observations_colnames = RMSmonthly, 
                desired_observation_colnames = RMSmonthly, suffix="RMS")

# # merge the two dataframes
# Eval_df = Eval_df_Palmes.merge(Eval_df_RMS, on="int_id", how="inner")
# Eval_df.to_csv(f"Eval_{cellsize}{suffix}test.csv", index=False)


# Pred_df = pd.read_csv(f"Pred_{cellsize}{suffix}.csv")               # Read Pred DataFrame
# create_traffic_emission_columns(df, traff_coeff=np.nan, TrI_coeff=np.nan, traffroadlength_coeff=np.nan, suffix="")

# create_Eval_df(grid_sp, gridID, point_observations, observationsID, observations_colnames, desired_observation_colnames = None, suffix = ""):


# Pred_df = pd.read_csv(f"Pred_{cellsize}{suffix}.csv")               # Read Pred DataFrame
# airpoll_grid_raster = xr.open_dataarray(f"AirPollDeterm_grid_{cellsize}.tif", engine="rasterio")[0] # Read raster data using rasterio
# onroadindices =  Pred_df.loc[Pred_df["ON_ROAD"] == 1, "int_id"].values
# onroadindices = onroadindices-1

# Pred_df["ROAD_NEIGHBOR"] = FindRoadNeighboringCells(airpoll_grid_raster, onroadindices)
# print(Pred_df.head(20))
# Pred_df.to_csv(f"Pred_{cellsize}{suffix}.csv", index=False)
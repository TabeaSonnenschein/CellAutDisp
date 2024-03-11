import xarray as xr
from xrspatial  import focal
from xrspatial.utils import ngjit
import numpy as np
import os
import pandas as pd
from data_preparation import FindRoadNeighboringCells

# Set the data folder and cell size
dataFolder = "D:/PhD EXPANSE/Data/Amsterdam"
os.chdir(os.path.join(dataFolder, "Air Pollution Determinants"))
cellsize = "25m"
suffix = "TrV_TrI_noTrA2"

Pred_df = pd.read_csv(f"Pred_{cellsize}{suffix}.csv")               # Read Pred DataFrame
airpoll_grid_raster = xr.open_dataarray(f"AirPollDeterm_grid_{cellsize}.tif", engine="rasterio")[0] # Read raster data using rasterio
onroadindices =  Pred_df.loc[Pred_df["ON_ROAD"] == 1, "int_id"].values
onroadindices = onroadindices-1

Pred_df["ROAD_NEIGHBOR"] = FindRoadNeighboringCells(airpoll_grid_raster, onroadindices)
print(Pred_df.head(20))
Pred_df.to_csv(f"Pred_{cellsize}{suffix}.csv", index=False)
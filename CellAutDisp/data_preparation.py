import xarray as xr
from xrspatial  import focal
from xrspatial.utils import ngjit
import numpy as np
import geopandas as gpd
from shapely.geometry import Point
from scipy.stats import mode

@ngjit
def ifNeighborOnRoad(kernel):
    if 1 in kernel:
        return 1
    else:
        return 0

def FindRoadNeighboringCells(raster, onroadindices):
    """This function takes a raster and a list of indices of cells on the road and 
    returns a list of 0 and 1, whereby 1 indicates that it is a cell neighboring the road.

    Args:
        raster (raster(xarray)): an xarray raster
        onroadindices (list(int)): a list of indices of cells on the road

    Returns:
        list(int): list of 0 and 1, whereby 1 indicates that it is a cell neighboring the road
    """
    onroads = np.asarray(raster[:]).flatten()
    onroads[:] = 0
    onroads[onroadindices] = 1
    raster[:]= onroads.reshape(raster.shape)
    raster[:] =  focal.apply(raster = raster, kernel= np.full((3,3), 1), func= ifNeighborOnRoad)
    roadsneighbors = np.asarray(raster[:]).flatten()
    roadsneighbors[onroadindices] = 0
    return roadsneighbors



def create_traffic_emission_columns(df, id, TrV_coeff=np.nan, TrI_coeff=np.nan, suffix=""):
    """Calculate traffic-related NO2 emissions based on traffic LUR coefficients and traffic data and the baseline NO2
    and produce the Predictor Dataframe (Pred_df) accordingly. The function also saves the Pred_df with the indicated suffix to a csv file.

    Parameters:
    - df (pd.DataFrame): Input DataFrame containing relevant columns.
    - id (str): Name of the column containing the unique identifier for each row.
    - TrV_coeff (float, optional): Coefficient for traffic volume. Default is NaN.
    - TrI_coeff (float, optional): Coefficient for traffic intensity. Default is NaN.

    Returns:
    pd.DataFrame: Updated DataFrame with additional columns for traffic-related NO2 emissions.

    Raises:
    None

    Notes:
    - The function modifies the input DataFrame in place.
    - Columns assumed in the DataFrame: 'road_length', 'baseline_NO2', 'ON_ROAD', and hourly traffic volumes.

    Example:
    >>> df = pd.DataFrame({'int_id': [1,2,3], 'TrV0_1': [10, 20, 30],  'baseline_NO2': [5, 5, 5], 'ON_ROAD': [1, 0, 1]})
    >>> updated_df = create_traffic_emission_columns(df, id= "int_id", TrV_coeff=2, TrI_coeff=0.5)
    """
    traffVolhours = ["TrV0_1","TrV1_2","TrV2_3","TrV3_4","TrV4_5","TrV5_6",
                     "TrV6_7","TrV7_8","TrV8_9","TrV9_10","TrV10_11","TrV11_12", 
                     "TrV12_13","TrV13_14","TrV14_15","TrV15_16","TrV16_17","TrV17_18",  
                     "TrV18_19","TrV19_20","TrV20_21","TrV21_22","TrV22_23","TrV23_24"]

    traffIntenshours = ["TrI0_1","TrI1_2","TrI2_3","TrI3_4","TrI4_5","TrI5_6",
                         "TrI6_7","TrI7_8","TrI8_9","TrI9_10","TrI10_11","TrI11_12", 
                         "TrI12_13","TrI13_14","TrI14_15","TrI15_16","TrI16_17","TrI17_18",  
                         "TrI18_19","TrI19_20","TrI20_21","TrI21_22","TrI22_23","TrI23_24"]

    TrafficNO2 = ["NO2_0_1_Traff","NO2_1_2_Traff","NO2_2_3_Traff","NO2_3_4_Traff", "NO2_4_5_Traff","NO2_5_6_Traff","NO2_6_7_Traff","NO2_7_8_Traff",
                  "NO2_8_9_Traff","NO2_9_10_Traff","NO2_10_11_Traff", "NO2_11_12_Traff","NO2_12_13_Traff","NO2_13_14_Traff", "NO2_14_15_Traff", "NO2_15_16_Traff",
                  "NO2_16_17_Traff","NO2_17_18_Traff", "NO2_18_19_Traff", "NO2_19_20_Traff","NO2_20_21_Traff","NO2_21_22_Traff", 
                  "NO2_22_23_Traff", "NO2_23_24_Traff"]

    TrafficNO2_nobaseline = ["NO2_0_1_TraffNoBase","NO2_1_2_TraffNoBase","NO2_2_3_TraffNoBase","NO2_3_4_TraffNoBase", "NO2_4_5_TraffNoBase","NO2_5_6_TraffNoBase","NO2_6_7_TraffNoBase","NO2_7_8_TraffNoBase",
                             "NO2_8_9_TraffNoBase","NO2_9_10_TraffNoBase","NO2_10_11_TraffNoBase", "NO2_11_12_TraffNoBase","NO2_12_13_TraffNoBase","NO2_13_14_TraffNoBase", "NO2_14_15_TraffNoBase", "NO2_15_16_TraffNoBase",
                             "NO2_16_17_TraffNoBase","NO2_17_18_TraffNoBase", "NO2_18_19_TraffNoBase", "NO2_19_20_TraffNoBase","NO2_20_21_TraffNoBase","NO2_21_22_TraffNoBase", 
                             "NO2_22_23_TraffNoBase", "NO2_23_24_TraffNoBase"]

    BaselineTrafficNO2 = ["NO2_0_1_basetraff","NO2_1_2_basetraff","NO2_2_3_basetraff","NO2_3_4_basetraff", "NO2_4_5_basetraff","NO2_5_6_basetraff","NO2_6_7_basetraff","NO2_7_8_basetraff",
                          "NO2_8_9_basetraff","NO2_9_10_basetraff","NO2_10_11_basetraff", "NO2_11_12_basetraff","NO2_12_13_basetraff","NO2_13_14_basetraff", "NO2_14_15_basetraff", "NO2_15_16_basetraff",
                          "NO2_16_17_basetraff","NO2_17_18_basetraff", "NO2_18_19_basetraff", "NO2_19_20_basetraff","NO2_20_21_basetraff","NO2_21_22_basetraff", 
                          "NO2_22_23_basetraff", "NO2_23_24_basetraff"]

    if  np.isnan(TrI_coeff) and not np.isnan(TrV_coeff):
        print("only Traffic Volume without traffic intensity")
        df[TrafficNO2_nobaseline] = df[traffVolhours] * TrV_coeff
    elif not np.isnan(TrI_coeff) and not np.isnan(TrV_coeff):
        print("with traffic intensity and traffic volume")
        TrVsubset = df[traffVolhours].copy() * TrV_coeff
        TrIsubset = df[traffIntenshours].copy() * TrI_coeff
        TrIsubset.columns = TrVsubset.columns
        df[TrafficNO2_nobaseline] = TrVsubset.add(TrIsubset, fill_value=0)
    elif not np.isnan(TrI_coeff) and np.isnan(TrV_coeff):
        print("only traffic intensity")
        df[TrafficNO2_nobaseline] = df[traffIntenshours] * TrI_coeff

    df.fillna(0, inplace=True)
    df[BaselineTrafficNO2] = df[TrafficNO2_nobaseline].add(df['baseline_NO2'].values, axis=0)
    df[TrafficNO2] = df[BaselineTrafficNO2]
    df.loc[df['ON_ROAD'] == 0, TrafficNO2] = 0
    df_final = df.loc[:,[id, "baseline_NO2","ON_ROAD"] + TrafficNO2_nobaseline + TrafficNO2 + BaselineTrafficNO2]
    print(df_final.head(20))
    df_final.to_csv(f"Pred_{suffix}.csv", index=False)
    return df_final


def create_Eval_df(grid_sp, gridID, point_observations, observationsID, observations_colnames, desired_observation_colnames = None, suffix = ""):
    """This function takes a grid and point observations and returns a DataFrame with the observations joined to the grid. 
    The function also saves the DataFrame (Eval_df) to a csv file.

    Args:
        grid_sp (geopandas.GeoDataFrame): a geopandas GeoDataFrame representing the grid
        gridID (str): the name of the grid ID column
        point_observations (geopandas.GeoDataFrame): a geopandas GeoDataFrame representing the point observations
        observationsID (str): the name of the observations ID column
        observations_colnames (list(str)): a list of the names of the observation columns
        desired_observation_colnames (list(str), optional): a list of the desired names of the observation columns. Default is None.
        suffix (str, optional): a suffix to be added to the csv file name. Default is "".

    Returns:
        pd.DataFrame: DataFrame (Eval_df) with the observations joined to the grid.
    """
    gridjoin = gpd.tools.sjoin(point_observations[[observationsID]+observations_colnames + ["geometry"]], grid_sp, how="inner", predicate='intersects')
    gridjoin = gridjoin.dropna(subset=['index_right'])
    gridjoin[gridID] = gridjoin["index_right"]
    gridjoin = gridjoin[[observationsID, gridID]+observations_colnames]

    # Take the mean of multiple observations
    freq_table = gridjoin[gridID].value_counts()
    multiple_observations = freq_table.index[freq_table >= 2]
    for i in multiple_observations:
        mean_values = gridjoin.loc[gridjoin[gridID] == i, observations_colnames].mean()
        gridjoin.loc[gridjoin[gridID] == i, observations_colnames] = mean_values.values
    gridjoin = gridjoin.drop_duplicates()
    eval_df = grid_sp.merge(gridjoin[[gridID] + observations_colnames], on=gridID, how="left")
    eval_df = eval_df[[gridID] + observations_colnames]
    if desired_observation_colnames is not None:
        eval_df = eval_df.rename(columns=dict(zip(observations_colnames, desired_observation_colnames)))
    eval_df.to_csv(f"Eval_{suffix}.csv", index=False)
    return eval_df


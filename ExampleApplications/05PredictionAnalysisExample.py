import os
import pandas as pd
import geopandas as gpd
from shapely.geometry.point import Point
from CellAutDisp import PrintSaveSummaryStats, MapSpatialDataFixedColorMapSetofVariables, ParallelMapSpatialDataFixedColorMap, ParallelMapSpatialData_StreetsFixedColorMap, ViolinOverTimeColContinous, SplitYAxis2plusLineGraph, meltPredictions, plotComputationTime,ViolinOverTimeColContinous_WithMaxSubgroups
from joblib import Parallel, delayed

###############################################################
### This script is an example of how to use the functions in the CellAutDisp package
### to create the analytics plots of the prediction results.
###############################################################

# Set the data folder
dataFolder = "/Users/tsonnens/Documents/CellAutDisp_pckg_data/test_data_CellAutDisp"
os.chdir(dataFolder)

cellsize = "50m"
predsuffix = "TrV_TrI_noTrA"
crs = 28992
stressor = "NO2"
unit = "(µg/m3)"

nr_cpus =6 # number of cores to use for parallel processing
parallelIfPossible = True

analysistype = [
    "StatusQuoPredMaps", 
    "StatusQuoPredMapsZoomed", 
    "ViolinPlotsStressors", 
    "ScenarioLinePlot",
    "ComputationTimeVisualisation"
    ]

addStreet = False
Neighborhoodextent = False

if any([x in analysistype for x in ["StatusQuoPredMaps", "StatusQuoPredMapsZoomed"]]):
    points = gpd.GeoSeries(
        [Point(485000, 120000), Point(485001, 120000)], crs=crs
    )  # Geographic WGS 84 - degrees
    points = points.to_crs(32619)  # Projected WGS 84 - meters
    distance_meters = points[0].distance(points[1])
    print(distance_meters)

    Predictions = pd.read_csv(f"{stressor}predictions_{cellsize}.csv")               # Read Pred DataFrame
    PrintSaveSummaryStats(Predictions, f"{stressor}predictions")

    AirPollGrid = gpd.read_file(f"AirPollDeterm_grid{cellsize}.shp")
    AirPollGrid_pred = AirPollGrid.merge(Predictions, on="int_id", how="left")
    months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov","Dec"]
    columnnames = [f"pred{stressor}_m{month}_h{hour}" for month in range(12) for hour in range(24)]
    labels = [f"{month} Hour {hour}-{hour+1}" for month in months for hour in range(24)]

    if "StatusQuoPredMaps" in analysistype:
        if parallelIfPossible:
            Parallel(n_jobs=nr_cpus)(delayed(ParallelMapSpatialDataFixedColorMap)(variable = variable, title = labels[columnnames.index(variable)] , rasterdf = AirPollGrid_pred, jointlabel = stressor, 
                                                vmin=0, vmax=65,distance_meters= distance_meters, cmap="turbo", suffix = cellsize) for variable in columnnames)
        else:
            MapSpatialDataFixedColorMapSetofVariables(variables = columnnames, rasterdf = AirPollGrid_pred, jointlabel = stressor, 
                                                specificlabel = labels, vmin=0, vmax=65,distance_meters= distance_meters, cmap="turbo") #cmaps jet, viridis, turbo, plasma, magma, inferno, cividis
    if "StatusQuoPredMapsZoomed" in analysistype:
        #############################################################
        if Neighborhoodextent:
            # 1) Defining extent based on neighborhood extent
            # zooming map into the extent of a specific neighborhood
            Neighborhoods = gpd.read_file("Amsterdam_Neighborhoods_RDnew.shp")
            suffix = "Bosleeuw"
            # suffix = "Duivendrecht"
            Neighborhood = Neighborhoods[Neighborhoods["buurtnaam"] == suffix]
            extent = Neighborhood.total_bounds
            print(extent)

        else:
            # # 2) Defining extent based on a specified bounding box
            # extent = [122500, 481500, 125500, 483500]
            # suffix = "specifiedBB_southeast"
            extent = [117800, 487700, 118800,  488600]
            suffix = "specifiedBB_Bosleeuw"

        # extracting the cells within the extent
        AirPollGrid_pred_extent = AirPollGrid_pred.cx[extent[0]:extent[2], extent[1]:extent[3]]

        if addStreet:
            # mapping cells plus streets with the extent
            streets = gpd.read_feather("Streets.feather")
            Parallel(n_jobs=nr_cpus)(delayed(ParallelMapSpatialData_StreetsFixedColorMap)(variable = variable, title = labels[columnnames.index(variable)] , 
                                                                                    rasterdf = AirPollGrid_pred_extent, streets = streets, jointlabel = stressor + " " + unit, 
                                                                                    vmin=0, vmax=65,distance_meters= distance_meters, cmap="turbo", suffix = cellsize + suffix) for variable in columnnames)
        else:
            # mapping the cells within the extent
            Parallel(n_jobs=nr_cpus)(delayed(ParallelMapSpatialDataFixedColorMap)(variable = variable, title = labels[columnnames.index(variable)] , rasterdf = AirPollGrid_pred_extent, jointlabel = stressor + " " + unit, 
                                                    vmin=0, vmax=65,distance_meters= distance_meters, cmap="turbo", suffix = cellsize + suffix) for variable in columnnames)

if "ViolinPlotsStressors" in analysistype:
    Predictions = pd.read_csv(f"{stressor}predictions_{cellsize}.csv")               # Read Pred DataFrame
    Predictions_melted = meltPredictions(Predictions, stressor, cellsize)
    ViolinOverTimeColContinous(xvar = "month", yvar=stressor, showplots= False, df = Predictions_melted, ylabel=stressor + " " + unit, xlabel = "Month", suffix = cellsize)
    ViolinOverTimeColContinous(xvar = "hour", yvar=stressor, showplots= False, df = Predictions_melted, ylabel=stressor + " " + unit, xlabel = "Hour", suffix = cellsize)

    # Violin plots for subsets of the data
    Pred_df = pd.read_csv(f"Pred_{cellsize}{predsuffix}.csv")               # Read Pred DataFrame
    Predictions_melted = Predictions_melted.merge(Pred_df[["int_id", "ON_ROAD","ROAD_NEIGHBOR"]], on="int_id", how="left")
    Predictions_melted_Onroad = Predictions_melted[Predictions_melted["ON_ROAD"] == 1]
    Predictions_melted_RoadNeighbor = Predictions_melted[Predictions_melted["ROAD_NEIGHBOR"] == 1]
    ViolinOverTimeColContinous(xvar = "month", yvar=stressor, showplots= False, df = Predictions_melted_Onroad, ylabel=stressor + " " + unit, xlabel = "Month", suffix= cellsize + "Onroad")
    ViolinOverTimeColContinous(xvar = "hour", yvar=stressor, showplots= False, df = Predictions_melted_Onroad, ylabel=stressor + " " + unit, xlabel = "Hour", suffix= cellsize +"Onroad")
    ViolinOverTimeColContinous(xvar = "month", yvar=stressor, showplots= False, df = Predictions_melted_RoadNeighbor, ylabel=stressor + " " + unit, xlabel = "Month", suffix= cellsize +"RoadNeighbor")
    ViolinOverTimeColContinous(xvar = "hour", yvar=stressor, showplots= False, df = Predictions_melted_RoadNeighbor, ylabel=stressor + " " + unit, xlabel = "Hour", suffix= cellsize +"RoadNeighbor")
   
if "ScenarioLinePlot" in analysistype:
    ScenarioPredictions = pd.read_csv(f"Scenario{stressor}predictions_{cellsize}.csv")
    ylimmin1 = ScenarioPredictions["Max"].min() -1
    ylimmax1 = ScenarioPredictions["Max"].max() + 1
    ylimmin2 = ScenarioPredictions["Mean"].min() - 1
    ylimmax2 = ScenarioPredictions["ON_ROAD_Mean"].max() + 1
    
    SplitYAxis2plusLineGraph(df = ScenarioPredictions, xvar="Scenarios",  yvar1_list = ["Max", "ROAD_NEIGHBOR_Max"], 
                             yvar2_list = ["Mean", "ON_ROAD_Mean", "ROAD_NEIGHBOR_Mean"], yvarlabel1_list= ["Max All Cells", "Max Road Neighbor"],
                             yvarlabel2_list= ["Mean All Cells", "Mean On Road", "Mean Road Neighbor"], ylimmin1 = ylimmin1,ylinmax1 = ylimmax1,
                            ylimmin2 = ylimmin2,ylinmax2 = ylimmax2,  xlabel = "Traffic Scenarios: Factor of Status Quo Traffic Volume",
                            ylabel1 = stressor + " " + unit, ylabel2 =  stressor + " " + unit, showplots=False, suffix= cellsize)

if "ComputationTimeVisualisation" in analysistype:
    CompTime_df = pd.read_csv(f"ComputationTime_{stressor}_{cellsize}.csv")
    plotComputationTime(CompTime_df, stressor, cellsize = cellsize)

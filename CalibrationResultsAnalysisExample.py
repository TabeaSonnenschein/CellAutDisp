from analytics import saveMatrixPlotsPerMonth, jointMatrixVisualisation, safeadjusterHistogram, SplitYAxis2plusLineGraph
import os
import pandas as pd
import json
from provide_adjuster import provide_adjuster

dataFolder = "D:/PhD EXPANSE/Data/Amsterdam/Air Pollution Determinants"
os.chdir(dataFolder)

cellsize = "25m"
matrixsize = 3
iter = False
meteolog = True

monthlyWeather2019 = pd.read_csv("monthlyWeather2019TempDiff.csv") # Read monthlyWeather2019 DataFrame
moderator_df = pd.read_csv(f"moderator_{cellsize}.csv")     # Read moderator DataFrame
with open(f"optimalparams_{cellsize}_scalingMS{matrixsize}iter{iter}MeteoLog{meteolog}.json", "r") as read_file:
        optimalparams = json.load(read_file)

new_folder = os.path.join(os.getcwd(), f"Analytics_{cellsize}_MS{matrixsize}iter{iter}MeteoLog{meteolog}")
if not os.path.exists(new_folder):
    os.makedirs(new_folder)
os.chdir(new_folder)
        
analytics = [
    "MonthlyMovingWindowMaps", 
    # "HourlyMonthlyPerformanceCharts", 
    # "MonthlyPerformanceCharts",
    # "AdjusterHistogram",
    ]

if "MonthlyMovingWindowMaps" in analytics:
    meteovalues_df= monthlyWeather2019[["Temperature", "Rain", "Windspeed", "Winddirection"]]
    os.chdir(os.path.join(dataFolder, f"TrV_TrI_noTrA weightmatrices {cellsize}"))
    saveMatrixPlotsPerMonth(matrixsize, optimalparams["meteoparams"], meteovalues_df, meteolog = False, suffix=f"_{cellsize}", addMeteodata=True)
    jointMatrixVisualisation(os.getcwd(), matrixsize, suffix = f"_{cellsize}")

if "HourlyMonthlyPerformanceCharts" in analytics:
    hourlymonthlyprefix = "RIVM"
    HourlyMonthly = pd.read_csv(os.path.join(dataFolder,f"{hourlymonthlyprefix}{cellsize}HourlyMonthlyPerformance.csv"))
    HourlyMonthly_clean = HourlyMonthly[['Month', 'Hour', 'R2', 'RMSE', 'ME']]
    HourlyMonthly_month = HourlyMonthly_clean.groupby('Month').mean()
    minR = HourlyMonthly_month["R2"].min()
    maxR = HourlyMonthly_month["R2"].max()
    SplitYAxis2plusLineGraph(df = HourlyMonthly_month, xvar="Month", yvar1_list = ["R2"], yvar2_list= ["RMSE", "ME"],
                         yvarlabel1_list = ["R2"], yvarlabel2_list = ["Root Mean Squared Error", "Mean Error"],  
                          ylimmin1 = minR-0.1,ylinmax1 = maxR+0.1,ylimmin2 = -25,ylinmax2 = 25, 
                         xlabel = "Performance per Month", 
                         ylabel1 = "R2", ylabel2 =  "Error (µg/m3)", suffix= f"_{hourlymonthlyprefix}{cellsize}")

    HourlyMonthly_hour = HourlyMonthly_clean.groupby('Hour').mean()
    print(HourlyMonthly_hour)
    minR = HourlyMonthly_hour["R2"].min()
    maxR = HourlyMonthly_hour["R2"].max()
    SplitYAxis2plusLineGraph(df = HourlyMonthly_hour, xvar="Hour", yvar1_list = ["R2"], yvar2_list= ["RMSE", "ME"],
                         yvarlabel1_list = ["R2"], yvarlabel2_list = ["Root Mean Squared Error", "Mean Error"],  
                         ylimmin1 = minR-0.1,ylinmax1 = maxR+0.1,ylimmin2 = -25,ylinmax2 = 25, 
                         xlabel = "Performance per Hour", 
                         ylabel1 = "R2", ylabel2 =  "Error (µg/m3)", suffix= f"_{hourlymonthlyprefix}{cellsize}")

if "MonthlyPerformanceCharts" in analytics:
    monthlyprefix = "Palmes"
    Monthly = pd.read_csv(os.path.join(dataFolder,f"{monthlyprefix}{cellsize}MonthlyPerformance.csv"))
    minR = Monthly["R2"].min()
    maxR = Monthly["R2"].max()
    SplitYAxis2plusLineGraph(df = Monthly, xvar="Month", yvar1_list = ["R2"], yvar2_list= ["RMSE", "ME"],
                     yvarlabel1_list = ["R2"], yvarlabel2_list = ["Root Mean Squared Error", "Mean Error"],  
                     ylimmin1 = minR-0.1,ylinmax1 = maxR+0.1,ylimmin2 = -10,ylinmax2 = 12, 
                     xlabel = "Performance per Month", 
                     ylabel1 = "R2", ylabel2 =  "Error (µg/m3)", suffix= f"_{monthlyprefix}{cellsize}")
    
if "AdjusterHistogram" in analytics:
    adjuster = provide_adjuster( morphparams = optimalparams["morphparams"], GreenCover = moderator_df["GreenCover"],
                                    openspace_fraction = moderator_df["openspace_fraction"], NrTrees = moderator_df["NrTrees"],
                                    building_height = moderator_df["building_height"], neigh_height_diff = moderator_df["neigh_height_diff"])
    safeadjusterHistogram(adjuster, suffix = f"_{cellsize}")
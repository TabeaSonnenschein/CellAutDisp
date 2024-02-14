from analytics import saveMatrixPlotsPerMonth, jointMatrixVisualisation, SplitYAxis2plusLineGraph
import os
import pandas as pd
import json

dataFolder = "D:/PhD EXPANSE/Data/Amsterdam"
os.chdir(os.path.join(dataFolder, "Air Pollution Determinants"))
cellsize = "50m"
matrixsize = 3
iter = False
meteolog = False
with open(f"optimalparams_{cellsize}_scalingMS{matrixsize}iter{iter}MeteoLog{meteolog}.json", "r") as read_file:
        optimalparams = json.load(read_file)
        
analytics = [
    # "MonthlyMovingWindowMaps", 
    "HourlyMonthlyPerformanceCharts", 
    "MonthlyPerformanceCharts"]

if "MonthlyMovingWindowMaps" in analytics:
    monthlyWeather2019 = pd.read_csv(os.path.join(dataFolder, "Weather", "monthlyWeather2019TempDiff.csv")) # Read monthlyWeather2019 DataFrame
    meteovalues_df= monthlyWeather2019[["Temperature", "Rain", "Windspeed", "Winddirection"]]
    os.chdir(os.path.join(dataFolder, f"Air Pollution Determinants\TrV_TrI_noTrA weightmatrices {cellsize}"))
    saveMatrixPlotsPerMonth(matrixsize, optimalparams["meteoparams"], meteovalues_df, meteolog = False, suffix=f"_{cellsize}", addMeteodata=True)
    jointMatrixVisualisation(os.getcwd(), matrixsize, suffix = f"_{cellsize}")

if "HourlyMonthlyPerformanceCharts" in analytics:
    hourlymonthlyprefix = "RIVM"
    HourlyMonthly = pd.read_csv(f"{hourlymonthlyprefix}{cellsize}HourlyMonthlyPerformance.csv")
    HourlyMonthly_clean = HourlyMonthly[['Month', 'Hour', 'R2', 'RMSE', 'ME']]
    HourlyMonthly_month = HourlyMonthly_clean.groupby('Month').mean()
    SplitYAxis2plusLineGraph(df = HourlyMonthly_month, xvar="Month", yvar1_list = ["R2"], yvar2_list= ["RMSE", "ME"],
                         yvarlabel1_list = ["R2"], yvarlabel2_list = ["Root Mean Squared Error", "Mean Error"],  ylimmin1 = 0.4,ylinmax1 = 0.8,ylimmin2 = -25,ylinmax2 = 25, 
                         xlabel = "Performance per Month", 
                         ylabel1 = "R2", ylabel2 =  "Error (µg/m3)", suffix= f"_{hourlymonthlyprefix}")

    HourlyMonthly_hour = HourlyMonthly_clean.groupby('Hour').mean()
    print(HourlyMonthly_hour)
    SplitYAxis2plusLineGraph(df = HourlyMonthly_hour, xvar="Hour", yvar1_list = ["R2"], yvar2_list= ["RMSE", "ME"],
                         yvarlabel1_list = ["R2"], yvarlabel2_list = ["Root Mean Squared Error", "Mean Error"],  ylimmin1 = 0.35,ylinmax1 = 0.8,ylimmin2 = -25,ylinmax2 = 25, 
                         xlabel = "Performance per Hour", 
                         ylabel1 = "R2", ylabel2 =  "Error (µg/m3)", suffix= f"_{hourlymonthlyprefix}")

if "MonthlyPerformanceCharts" in analytics:
    monthlyprefix = "Palmes"
    Monthly = pd.read_csv(f"{monthlyprefix}{cellsize}MonthlyPerformance.csv")
    SplitYAxis2plusLineGraph(df = Monthly, xvar="Month", yvar1_list = ["R2"], yvar2_list= ["RMSE", "ME"],
                     yvarlabel1_list = ["R2"], yvarlabel2_list = ["Root Mean Squared Error", "Mean Error"],  ylimmin1 = 0.3,ylinmax1 = 0.5,ylimmin2 = -10,ylinmax2 = 12, 
                     xlabel = "Performance per Month", 
                     ylabel1 = "R2", ylabel2 =  "Error (µg/m3)", suffix= f"_{monthlyprefix}")
from analytics import saveMatrixPlotsPerMonth, jointMatrixVisualisation
import os
import pandas as pd

dataFolder = "D:/PhD EXPANSE/Data/Amsterdam"
os.chdir(os.path.join(dataFolder, "Air Pollution Determinants"))
monthlyWeather2019 = pd.read_csv(os.path.join(dataFolder, "Weather", "monthlyWeather2019TempDiff.csv")) # Read monthlyWeather2019 DataFrame


meteovalues_df= monthlyWeather2019[["Temperature", "Rain", "Windspeed", "Winddirection"]]
meteoparams = [0.409800614, 0.011336538, 0.162193556, -0.096161606,  0.674606756, 0.830105679, 0.304843606, 0.077548563, 4.926544219]
# meteoparams = [0.232669543,1.820935633,1.716740457,1.961315493,1.640064053,0.077584399, 1.825339797,1.392984166,0.158231089]
# meteoparams = [ 0.98962192, 1.99499355, 1.86909367, 1.94074353, 0.25499547,  1.19864123, 1.64563954, 1.23736286, 0.05472525]

matrixsize = 7
cellsize = "50m"
os.chdir(os.path.join(dataFolder, f"Air Pollution Determinants\TrV_TrI_noTrA weightmatrices {cellsize}"))

saveMatrixPlotsPerMonth(matrixsize, meteoparams, meteovalues_df, meteolog = False, suffix=f"_{cellsize}", addMeteodata=True)
jointMatrixVisualisation(os.getcwd(), matrixsize, suffix = f"_{cellsize}")



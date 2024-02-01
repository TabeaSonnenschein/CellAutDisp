from create_weighted_matrix import saveMatrixPlotsPerMonth
import os
import pandas as pd

dataFolder = "D:/PhD EXPANSE/Data/Amsterdam"
os.chdir(os.path.join(dataFolder, "Air Pollution Determinants"))
monthlyWeather2019 = pd.read_csv(os.path.join(dataFolder, "Weather", "monthlyWeather2019TempDiff.csv")) # Read monthlyWeather2019 DataFrame


meteovalues_df= monthlyWeather2019[["Temperature", "Rain", "Windspeed", "Winddirection"]]
# meteoparams = [0.08212756, 1.648357618, 0.931894172, 1.169432227, 1.248785641, 
#                0.071074995, 1.599493585, 0.435126242,2.529250082]
meteoparams = [0.11200939,  0.90760653, -0.84446405,  1.65036327 , 0.99530872,  
               0.41819684,  0.52935772,  0.38716983,  1.29562063]
matrixsize = 5

saveMatrixPlotsPerMonth(matrixsize, meteoparams, meteovalues_df, meteolog = False, suffix="newcalib")
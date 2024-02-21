import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib import gridspec
import os
from create_weighted_matrix import returnCorrectWeightedMatrix
import numpy as np
from provide_adjuster import provide_adjuster
from calibration import compute_hourly_dispersion
import pandas as pd
import seaborn as sns
from matplotlib_scalebar.scalebar import ScaleBar

def plotWeightedMatrix(matrixsize, meteoparams, meteovalues, meteolog, suffix = "", show = False, addMeteodata = False):
    """This function plots the weighted matrix.

    Args:
        matrixsize (int): An odd integer that determines the size of the matrix
        meteoparams (list(float)): parameterlist from the calibration module
        meteovalues (list(float)): a list of meteorological values order as: temperature, rain, windspeed, winddirection
        meteolog (Boolean): if True, the log of the meteorological values is taken apart from winddirection
        suffix (str, optional): An string extension to the filename (e.g. months, matrixsize, any specification). Defaults to "".
        show (bool, optional): indicating whether to show the plot or not.  Defaults to False.
    
    Returns:
        None
    """
    weight_matrix = returnCorrectWeightedMatrix(meteolog, matrixsize, meteoparams, meteovalues)
    plt.imshow(weight_matrix)
    plt.colorbar()
    if addMeteodata:
        plt.subplots_adjust(bottom=0.2)
        plt.text(0.5, -0.15, f"Temperature: {round(meteovalues[0],2)} C°, Rain: {round(meteovalues[1],1)} mm,\n Windspeed: {round(meteovalues[2],2)} m/s, Winddirection: {round(meteovalues[3],2)}° (red arrow)",
                 ha='center', va='center', transform=plt.gca().transAxes)
        
        # Draw a line to the center of the weight matrix from the wind direction
        center_x, center_y = np.array(weight_matrix.shape) // 2
        wind_dir_rad = np.deg2rad( ((meteovalues[3] + 360) % 360)-90)
        arrow_length = matrixsize / 3  # Adjust the length of the arrow as needed
        arrow_dx = arrow_length * np.cos(wind_dir_rad)
        arrow_dy = arrow_length * np.sin(wind_dir_rad)
        arrow = patches.FancyArrowPatch((center_x, center_y), (center_x + arrow_dx, center_y + arrow_dy),
                                color='red', arrowstyle='<-', linewidth=2.5, mutation_scale=15)
        plt.gca().add_patch(arrow)
    plt.savefig(f"weighted_matrix{suffix}.png",bbox_inches='tight', dpi = 300)
    if show:
        plt.show()
    plt.close()
        

def saveMatrixPlotsPerMonth(matrixsize, meteoparams, meteovalues_df, meteolog = False, suffix = "", addMeteodata = False):
    """This function saves the weighted matrix plots for each month. The addMeteodata boolean parameter sets whether to add the 
    meteorological data as text to the plot. it also adds and arrow to the plot to indicate the wind direction.

    Args:
        matrixsize (int): An odd integer that determines the size of the matrix
        meteoparams (list(float)): parameterlist from the calibration module
        meteovalues_df (dataframe(float)): A dataframe of all meteorological values for each month (months are rows). The dataframe should have the columns "Temperature", "Rain", "Windspeed", "Winddirection" in that order.
        meteolog (Boolean): if True, the log of the meteorological values is taken apart from winddirection

    """
    for month in range(12):
        meteovalues = meteovalues_df.iloc[month].values
        plotWeightedMatrix(matrixsize, meteoparams, meteovalues, meteolog, 
                           suffix = f"MS{matrixsize}_M{month+1}{suffix}", show = False, 
                           addMeteodata=addMeteodata)



def jointMatrixVisualisation(figures_directory, matrixsize, suffix = ""):
    """This function creates a combined figure of the weighted matrices for each month.

    Args:
        figures_directory (str): the directory where the weighted matrices are saved
        matrixsize (int): the size of the matrix
        suffix (str, optional): An string extension to the filename (e.g. months, matrixsize, any specification). Defaults to "".
    """
    num_rows = 4
    num_cols = 3
    # Set up the overall figure with gridspec
    fig = plt.figure(figsize=(16, 20))  # Adjust the figure size as needed
    gs = gridspec.GridSpec(num_rows, num_cols, width_ratios=[1, 1, 1])

    for month in range(12):
        image = plt.imread(os.path.join(figures_directory, f"weighted_matrixMS{matrixsize}_M{month+1}{suffix}.png"))
        ax = plt.subplot(gs[month // num_cols, month % num_cols])
        ax.imshow(image)
        ax.set_xticks([])
        ax.set_yticks([])
        ax.set_title(f'Month {month + 1}')

    plt.tight_layout()
    plt.savefig(f"combined_weightmatices_MS{matrixsize}_{suffix}.png", dpi = 500)  # Save the combined figure
    plt.close()


def estimateMonthlyHourlyValues(raster, TrafficNO2perhour, baselineNO2, onroadindices, matrixsize, meteoparams, 
                       repeatsparams, meteovalues_df, morphparams = None, scalingparams = [1,1,1], 
                       moderator_df = None, iter = True, baseline = False, meteolog = False, 
                       stressor = "NO2"):
    """This function estimates the stressor values for each hour and month and returns a dataframe with the predictions. It will select the correct dispersion model
    based on the input parameters.
    
    Args:
        raster (xarray raster): the raster that is used for the dispersion model (xarray format (see package doc)) .
        TrafficNO2perhour (dataframe(float)): The dataframe with the hourly traffic NO2 values for each raster cell. Only the cells on roads should have values the rest default to 0.
        baselineNO2 (vector(float)): The list of baseline NO2 values for each raster cell.
        onroadindices (list(int)): A list of the indices of the cells that are on roads.
        matrixsize (int): And odd integer that specifies the size of the matrix that is used for the dispersion model.
        meteoparams (list(float)): A list of calibrated meteorological parameters that are used for the weighted matrix.
        repeatsparams (list(float)): A list of calibrated parameters that are used for the number of repeats of the focal operation. This could be a single value or a value that is dependent on the meteorological values.
        meteovalues_df (dataframe(float)): A dataframe of all meteorological values for each month (months are rows). The dataframe should have the columns "Temperature", "Rain", "Windspeed", "Winddirection" in that order.
        morphparams (list(float), optional): A list of calibrated parameters that are used for the morphological adjuster. Defaults to None.
        scalingparams (list(float), optional): A calibrated parameter list for scaling the traffic values and baseline NO2. Defaults to [1,1,1], which means no scaling in effect.
        moderator_df (_type_, optional): Contains the morphological moderator variables that are used for the adjuster. Defaults to None.
        iter (bool, optional): If the adjuster should be applied in an iterative manner during the iterative applications of the focal operation (iter = True) or afterwards once (iter = False). Defaults to True.
        baseline (bool, optional): Argument onto whether to apply a scaling based on the baseline and traffic coefficients. Defaults to False.
        meteolog (boolean): if True, the log of the meteorological values is taken apart from winddirection. Defaults to False.
        stressor (str, optional): The stressor for which the predictions are made. Defaults to "NO2".
    
    Returns:
        dataframe: A dataframe with the predictions for each hour and month.
    """
    Results_df = pd.DataFrame({"int_id": range(1,len(baselineNO2)+1), "baselineNO2": baselineNO2})
    if morphparams is not None:
        adjuster = provide_adjuster( morphparams = morphparams, GreenCover = moderator_df["GreenCover"], openspace_fraction = moderator_df["openspace_fraction"], 
                            NrTrees =  moderator_df["NrTrees"], building_height = moderator_df["building_height"], 
                            neigh_height_diff = moderator_df["neigh_height_diff"])
    else:
        adjuster = None
    preds,colnames = [], []
    for month in range(12):
        print("Computing Month: ", month + 1)
        weightmatrix = returnCorrectWeightedMatrix(meteolog, matrixsize, meteoparams= meteoparams, meteovalues = meteovalues_df.iloc[month].values)
        if len(repeatsparams) > 1:
            nr_repeats = repeatsparams[0] + (repeatsparams[1] * meteovalues_df.iloc[month, 2])
        else: 
            nr_repeats = int(repeatsparams[0])        
        for hour in range(24):
            Pred =  compute_hourly_dispersion(raster = raster, TrafficNO2 = TrafficNO2perhour.iloc[:,hour], baselineNO2 = baselineNO2,
                                                  onroadindices = onroadindices, weightmatrix = weightmatrix, nr_repeats = nr_repeats,
                                                  adjuster=adjuster, iter = iter, baseline = baseline, baseline_coeff = scalingparams[0], 
                                                traffemissioncoeff_onroad = scalingparams[1],traffemissioncoeff_offroad = scalingparams[2])

            preds.append(list(Pred))
            colnames.append(f"pred{stressor}_m{month}_h{hour}")

    # creating a dataframe with the predictions and the columnnames
    preds = list(map(list, zip(*preds)))
    Results_df = pd.concat([Results_df, pd.DataFrame(preds, columns=colnames)], axis=1)
    return Results_df

def saveMonthlyHourlyredictions(raster, TrafficNO2perhour, baselineNO2, onroadindices, matrixsize, meteoparams, 
                       repeatsparams, meteovalues_df, morphparams = None, scalingparams = [1,1,1], 
                       moderator_df = None, iter = True, baseline = False, 
                       meteolog = False, suffix = "", stressor = "NO2"):
    """This function saves the NO2 predictions per hour and month to a csv file and print the summary statistics of the predictions. It will select the correct dispersion model 
    based on the input parameters.
    
    Args:
        raster (xarray raster): the raster that is used for the dispersion model (xarray format (see package doc)) .
        TrafficNO2perhour (dataframe(float)): The dataframe with the hourly traffic NO2 values for each raster cell. Only the cells on roads should have values the rest default to 0.
        baselineNO2 (vector(float)): The list of baseline NO2 values for each raster cell.
        onroadindices (list(int)): A list of the indices of the cells that are on roads.
        matrixsize (int): And odd integer that specifies the size of the matrix that is used for the dispersion model.
        meteoparams (list(float)): A list of calibrated meteorological parameters that are used for the weighted matrix.
        repeatsparams (list(float)): A list of calibrated parameters that are used for the number of repeats of the focal operation. This could be a single value or a value that is dependent on the meteorological values.
        meteovalues_df (dataframe(float)): A dataframe of all meteorological values for each month (months are rows). The dataframe should have the columns "Temperature", "Rain", "Windspeed", "Winddirection" in that order.
        morphparams (list(float), optional): A list of calibrated parameters that are used for the morphological adjuster. Defaults to None.
        scalingparams (list(float), optional): A calibrated parameter list for scaling the traffic values and baseline NO2. Defaults to [1,1,1], which means no scaling in effect.
        moderator_df (_type_, optional): Contains the morphological moderator variables that are used for the adjuster. Defaults to None.
        iter (bool, optional): If the adjuster should be applied in an iterative manner during the iterative applications of the focal operation (iter = True) or afterwards once (iter = False). Defaults to True.
        baseline (bool, optional): Argument onto whether to apply a scaling based on the baseline and traffic coefficients. Defaults to False.
        meteolog (boolean): if True, the log of the meteorological values is taken apart from winddirection. Defaults to False.
        suffix (str, optional): A string extension to the filename (e.g. cellsize, matrixsize, any specification). Defaults to "".
        stressor (str, optional): The stressor for which the predictions are made. Defaults to "NO2".
    """
    Results_df = estimateMonthlyHourlyValues(raster, TrafficNO2perhour, baselineNO2, onroadindices, matrixsize, meteoparams, 
                       repeatsparams, meteovalues_df, morphparams, scalingparams, 
                       moderator_df, iter, baseline, meteolog)
    Results_df.to_csv(f"{stressor}predictions_{suffix}.csv", index = False)
    return Results_df
    

def makeScenarioPredictsblank(Scenarios, cellsubgroups = None):
    ScenarioPredictions  = pd.DataFrame({"Scenarios": Scenarios, "Mean": np.nan, "Max": np.nan, "Min": np.nan})
    if cellsubgroups is not None:
        for celltype in cellsubgroups.columns[1:]:
            ScenarioPredictions[f"{celltype}_Mean"] = np.nan
            ScenarioPredictions[f"{celltype}_Max"] = np.nan
            ScenarioPredictions[f"{celltype}_Min"] = np.nan
    return ScenarioPredictions

def calculateScenarioSummaryStats(Pred, scenario, columnnames, ScenarioPredictions, cellsubgroups = None):
    """ This function calculates the summary statistics for the predictions of a scenario and adds them to the ScenarioPredictions dataframe.
    It will also calculate the summary statistics for different cell subgroups if the cellsubgroups dataframe is provided.
    
    Args:
        Pred (dataframe(float)): A dataframe with the predictions for each hour and month.
        scenario (float): The scenario for which the predictions are made.
        columnnames (list(str)): A list of the column names of the predictions.
        ScenarioPredictions (dataframe(float)): A dataframe with the summary statistics for the different scenarios.
        cellsubgroups (dataframe(int), optional): Defaults to None. A dataframe with the "int_id" and the different cell subgroups
    
    Returns:
        dataframe: A dataframe with the summary statistics for the different scenarios.
    """
    index = ScenarioPredictions[ScenarioPredictions['Scenarios'] == scenario].index[0]
    cellvals = Pred.loc[:, columnnames].values.flatten()
    ScenarioPredictions.loc[index, "Mean"] =  np.mean(cellvals)
    ScenarioPredictions.loc[index, "Max"] =  max(cellvals)
    ScenarioPredictions.loc[index, "Min"] =  min(cellvals)
    if cellsubgroups is not None:
        Pred = Pred.merge(cellsubgroups, on="int_id", how="left")
        for celltype in cellsubgroups.columns[1:]:
            cellvals = Pred.loc[Pred[celltype] == 1, columnnames].values.flatten()
            ScenarioPredictions.loc[index, f"{celltype}_Mean"] =  np.mean(cellvals)
            ScenarioPredictions.loc[index, f"{celltype}_Max"] =  max(cellvals)
            ScenarioPredictions.loc[index, f"{celltype}_Min"] =  min(cellvals)
    return ScenarioPredictions


def saveTrafficScenarioPredictions(trafficfactors, raster, TrafficNO2perhour, 
                                   baselineNO2, onroadindices, 
                                    matrixsize, meteoparams, repeatsparams, meteovalues_df, 
                                    morphparams = None, scalingparams = [1,1,1], 
                                    moderator_df = None, iter = True, baseline = False, 
                                    meteolog = False, suffix = "", stressor = "NO2", cellsubgroups = None):
    """This function saves the NO2 predictions for a set of simple traffic scenarios to a csv file
    and print the summary statistics of the predictions. The trafficscenarios are simple adjustments of 
    the traffic and onroad NO2 by the specified factors. The trafficfactors parameters is that list of factors for the traffic scenarios.
    The function will select the correct dispersion model based on the input parameters. It moreover saves the summary
    statistics of the predictions for different cell subgroups (e.g. ON_ROAD, ROAD_NEIGHBOR) in a csv file.
    
    Args:
        trafficfactors (list(float)): A list of factors for which to test the traffic scenarios. The scenario will be the on-road traffic NO2 multiplied by the different factors.
        raster (xarray raster): the raster that is used for the dispersion model (xarray format (see package doc)) .
        TrafficNO2perhour (dataframe(float)): The dataframe with the hourly traffic NO2 values for each raster cell. Only the cells on roads should have values the rest default to 0.
        baselineNO2 (vector(float)): The list of baseline NO2 values for each raster cell.
        onroadindices (list(int)): A list of the indices of the cells that are on roads.
        matrixsize (int): And odd integer that specifies the size of the matrix that is used for the dispersion model.
        meteoparams (list(float)): A list of calibrated meteorological parameters that are used for the weighted matrix.
        repeatsparams (list(float)): A list of calibrated parameters that are used for the number of repeats of the focal operation. This could be a single value or a value that is dependent on the meteorological values.
        meteovalues_df (dataframe(float)): A dataframe of all meteorological values for each month (months are rows). The dataframe should have the columns "Temperature", "Rain", "Windspeed", "Winddirection" in that order.
        morphparams (list(float), optional): A list of calibrated parameters that are used for the morphological adjuster. Defaults to None.
        scalingcoeffs (list(float), optional): A calibrated parameter list for scaling the traffic values and baseline NO2. Defaults to [1,1,1], which means no scaling in effect.
        moderator_df (_type_, optional): Contains the morphological moderator variables that are used for the adjuster. Defaults to None.
        iter (bool, optional): If the adjuster should be applied in an iterative manner during the iterative applications of the focal operation (iter = True) or afterwards once (iter = False). Defaults to True.
        baseline (bool, optional): Argument onto whether to apply a scaling based on the baseline and traffic coefficients. Defaults to False.
        meteolog (boolean): if True, the log of the meteorological values is taken apart from winddirection. Defaults to False.
        suffix (str, optional): A string extension to the filename (e.g. cellsize, matrixsize, any specification). Defaults to "".
        stressor (str, optional): The stressor for which the predictions are made. Defaults to "NO2".
        cellsubgroups (dataframe(int), optional): Defaults to None. A dataframe with the "int_id" and the different cell subgroups
    """
    ScenarioPredictions = makeScenarioPredictsblank(Scenarios = trafficfactors, cellsubgroups = cellsubgroups)
    columnnames = [f"pred{stressor }_m{month}_h{hour}" for month in range(12) for hour in range(24)]
    for scenario in trafficfactors:
        print("Computing Scenario: ", scenario)
        trafficscenarios = TrafficNO2perhour * scenario
        Pred = saveMonthlyHourlyredictions(raster = raster, TrafficNO2perhour = trafficscenarios, 
                                        baselineNO2 = baselineNO2,
                                        onroadindices = onroadindices, matrixsize=matrixsize, 
                                        meteoparams=meteoparams, repeatsparams=repeatsparams, 
                                        meteovalues_df=meteovalues_df,
                                        morphparams = morphparams, scalingparams = scalingparams, 
                                        moderator_df = moderator_df, iter = iter, baseline = baseline, 
                                        meteolog = meteolog, suffix = suffix + f"_traffScenario_{scenario}", 
                                        stressor = stressor)
        ScenarioPredictions = calculateScenarioSummaryStats(Pred, scenario, columnnames, 
                                      ScenarioPredictions, cellsubgroups)
    ScenarioPredictions.to_csv(f"Scenario{stressor}predictions_{suffix}.csv", index=False)
    return ScenarioPredictions



def PrintSaveSummaryStats(df, dfname, suffix = ""):
    """Print and save summary statistics of the dataframe"""
    descript = df.describe()
    descript.loc[len(descript.index)]= [np.percentile(df[col], 10) for col in df.columns]
    descript.loc[len(descript.index)]= [np.percentile(df[col], 20) for col in df.columns]
    descript.loc[len(descript.index)]= [np.percentile(df[col], 30) for col in df.columns]
    descript.loc[len(descript.index)]= [np.percentile(df[col], 40) for col in df.columns]
    descript.loc[len(descript.index)]= [np.percentile(df[col], 50) for col in df.columns]
    descript.loc[len(descript.index)]= [np.percentile(df[col], 60) for col in df.columns]
    descript.loc[len(descript.index)]= [np.percentile(df[col], 70) for col in df.columns]
    descript.loc[len(descript.index)]= [np.percentile(df[col], 80) for col in df.columns]
    descript.loc[len(descript.index)]= [np.percentile(df[col], 90) for col in df.columns]
    #rename the rows
    descript= descript.set_axis(["count", "mean", "std", "min", "25%", "50%", "75%", "max", "pth10", 
                     "pth20", "pth30", "pth40", "pth50", "pth60", "pth70", "pth80", "pth90"], axis='index')
    descript.to_csv(f"{dfname}_{suffix}_descript.csv")
    print(descript)


def SingleVarViolinplot(df,variable, ylabel = None, filesuffix = ""):
    if ylabel == None:
        ylabel = variable
    sns.set(style="whitegrid")
    plt.figure(figsize=(6, 6))
    sns.violinplot(y=variable, data=df, linewidth=0, color= "#009999")
    plt.xlabel("Across Space")
    plt.ylabel(ylabel)
    plt.title(f"Violin Plot of Baseline NO2 Distribution")
    plt.savefig(f'Violinplot_{variable}{filesuffix}.png', dpi = 400)
    plt.close()


def ViolinOverTimeColContinous(xvar, yvar, showplots, df, ylabel = None, xlabel = None, suffix = ""):
    if ylabel is None:
        ylabel = yvar
    if xlabel is None:
        xlabel = xvar
    mean_values_per_x = pd.DataFrame(df.groupby(xvar)[yvar].mean())
    mean_values_per_x.reset_index(inplace=True)
    mean_values_per_x["index"] = mean_values_per_x.index
    max_values_per_x = pd.DataFrame(df.groupby(xvar)[yvar].max())
    max_values_per_x.reset_index(inplace=True)
    max_values_per_x["index"] = max_values_per_x.index
    df = df.sort_values(by=[xvar])
    sns.set(style="whitegrid")
    plt.figure(figsize=(10, 6))
    sns.violinplot(x=xvar, y=yvar, color= "#009999", data=df, linewidth=0, order=mean_values_per_x[xvar])
    sns.lineplot(x="index", y=yvar, data=mean_values_per_x, color = "black", legend= "brief", label = "Mean")
    sns.lineplot(x="index", y=yvar, data=max_values_per_x, color = "#C00000", legend= "brief", label = "Max")    
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.title(f"Distribution of {ylabel} By {xlabel}")
    plt.savefig(f'{yvar}_violinplot_by_{xvar}_{suffix}.png', dpi = 400)
    if showplots:
        plt.show()
    plt.close()

def MapSpatialData(variable, df, label, AirPollGrid,filesuffix = None):
    AirPollGrid = AirPollGrid.merge(df[["int_id", variable]], on="int_id", how="left")
    print(AirPollGrid[variable].describe())
    AirPollGrid.plot(variable, cmap= "viridis", antialiased=False, linewidth = 0.00001, legend = True)
    plt.title(f"{label} Distribution")
    plt.savefig(f'{variable}_map_{filesuffix}.png',bbox_inches='tight', dpi=400)
    plt.close()


def MapSpatialDataFixedColorMapSetofVariables(variables, rasterdf, jointlabel, specificlabel, vmin, vmax, 
                                              distance_meters, cmap= "viridis" , suffix = ""):
    for variable in variables:
        print(rasterdf[variable].describe())
        ax= rasterdf.plot(variable, cmap= cmap, antialiased=False, linewidth = 0.00001, legend = True, vmin = vmin, vmax=vmax)
        ax.set_xlim(rasterdf.total_bounds[0], rasterdf.total_bounds[2])
        ax.set_ylim(rasterdf.total_bounds[1], rasterdf.total_bounds[3])
        scalebar = ScaleBar(distance_meters, length_fraction=0.2, location="lower right", box_alpha=0.5)  # Adjust the length as needed
        ax.add_artist(scalebar)
        # ax.axis('off')
        plt.title(f"{jointlabel} Distribution: {specificlabel[variables.index(variable)]}")
        plt.savefig(f'{variable}_map_{suffix}.png', bbox_inches='tight',dpi=400)
        plt.close()

def ParallelMapSpatialDataFixedColorMap(variable, title, rasterdf, jointlabel, vmin, vmax, distance_meters, cmap= "viridis" , suffix = ""):
    print(rasterdf[variable].describe())
    ax= rasterdf.plot(variable, cmap= cmap, antialiased=False, linewidth = 0.00001, legend = True, vmin = vmin, vmax=vmax)
    ax.set_xlim(rasterdf.total_bounds[0], rasterdf.total_bounds[2])
    ax.set_ylim(rasterdf.total_bounds[1], rasterdf.total_bounds[3])
    scalebar = ScaleBar(distance_meters, length_fraction=0.2, location="lower right", box_alpha=0.5)  # Adjust the length as needed
    ax.add_artist(scalebar)
    # ax.axis('off')
    plt.title(f"{jointlabel} Distribution: {title}")
    plt.savefig(f'{variable}_map_{suffix}.png',bbox_inches='tight', dpi=400)
    plt.close()

def ParallelMapSpatialData_StreetsFixedColorMap(variable, title, rasterdf, streets, jointlabel, vmin, vmax, distance_meters, cmap= "viridis" , suffix = ""):
    print(rasterdf[variable].describe())
    ax= rasterdf.plot(variable, cmap= cmap, antialiased=False, linewidth = 0.00001, legend = True, vmin = vmin, vmax=vmax)
    ax.set_xlim(rasterdf.total_bounds[0], rasterdf.total_bounds[2])
    ax.set_ylim(rasterdf.total_bounds[1], rasterdf.total_bounds[3])
    scalebar = ScaleBar(distance_meters, length_fraction=0.2, location="lower right", box_alpha=0.5)  # Adjust the length as needed
    ax.add_artist(scalebar)
    # add the streets layer in black to the map
    streets.plot(ax=ax, color="black", linewidth=0.5)
    # ax.axis('off')
    plt.title(f"{jointlabel} Distribution: {title}")
    plt.savefig(f'{variable}_map_{suffix}.png',bbox_inches='tight', dpi=400)
    plt.close()



def ScatterplotContinuous(df, yvariable, xvariable, ylabel = None, xlabel = None):
    if ylabel == None:
        ylabel = yvariable
    if xlabel == None:
        xlabel = xvariable
    mean_values_per_hour = pd.DataFrame(df.groupby(xvariable)[yvariable].mean())
    mean_values_per_hour["hour"] = mean_values_per_hour.index
    sns.set(style="whitegrid")
    plt.figure(figsize=(6, 6))
    sns.scatterplot(x=xvariable, y=yvariable, data=df, alpha=0.005, color = "#009999", edgecolor = "none")
    sns.lineplot(x=xvariable, y=yvariable, data=mean_values_per_hour, color = "#C00000", legend= "brief", label = "Mean")
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.title(f"Scatterplot of {yvariable} by {xvariable}")
    plt.savefig(f'Scatterplot_{yvariable}by{xvariable}.png', dpi = 400)
    plt.close()


def SplitYAxisLineGraph(df, xvar, yvar1, yvar2, yvarlabel1, yvarlabel2,  ylimmin1,ylinmax1,ylimmin2,ylinmax2, xlabel, ylabel1, ylabel2, showplots = False):
    f, (ax, ax2) = plt.subplots(2, 1, sharex=True)
    sns.lineplot(ax=ax, x=xvar, y=yvar1, data=df, color = "#C00000", legend= "brief", label = yvarlabel1)
    sns.lineplot(ax=ax2, x=xvar, y=yvar2, data=df, color = "#009999", legend= "brief", label = yvarlabel2)
    plt.xlabel(xlabel)
    ax.set_ylim(ylimmin1, ylinmax1)  # most of the data
    ax2.set_ylim(ylimmin2, ylinmax2)  # outliers only
    ax.set_ylabel(ylabel1)
    ax2.set_ylabel(ylabel2)
    ax.spines['bottom'].set_visible(False)
    ax2.spines['top'].set_visible(False)
    ax.xaxis.tick_top()
    ax.tick_params(labeltop=False)  # don't put tick labels at the top
    ax2.xaxis.tick_bottom()
    plt.savefig(f'{yvar1}_and_{yvar2}_by_{xvar}.png', dpi = 400)
    if showplots:
        plt.show()
    plt.close()
    

def SplitYAxis2plusLineGraph(df, xvar, yvar1_list, yvar2_list, yvarlabel1_list, yvarlabel2_list, 
                             ylimmin1, ylinmax1, ylimmin2, ylinmax2, xlabel, ylabel1, 
                             ylabel2, showplots=False, suffix=""):
    f, (ax, ax2) = plt.subplots(2, 1, sharex=True)
    ax2.axhline(y=0, linestyle='--', color='gray', linewidth=0.6)
    ax.axhline(y=0, linestyle='--', color='gray', linewidth=0.6)
    
    # Plot the first y variable
    for i, yvar1 in enumerate(yvar1_list):
        color = ["#C00000", "#001180", "#834C84"][i]
        sns.lineplot(ax=ax, x=xvar, y=yvar1, data=df, color=color, legend="brief", label=yvarlabel1_list[i])


    # Plot multiple lines for the second y variable
    for i, yvar2 in enumerate(yvar2_list):
        # color = sns.color_palette("husl", len(yvar2_list))[i]
        color = ["#009999", "black", "#847B02", "#001180"][i]
        sns.lineplot(ax=ax2, x=xvar, y=yvar2, data=df, color=color, legend="brief", label=yvarlabel2_list[i])

    plt.xlabel(xlabel)
    ax.set_ylim(ylimmin1, ylinmax1)  # most of the data
    ax2.set_ylim(ylimmin2, ylinmax2)  # outliers only
    ax.set_ylabel(ylabel1)
    ax2.set_ylabel(ylabel2)

    # Remove unnecessary spines and ticks
    ax.spines['bottom'].set_visible(False)
    ax2.spines['top'].set_visible(False)
    ax.xaxis.tick_top()
    ax.tick_params(labeltop=False)  # don't put tick labels at the top
    ax2.xaxis.tick_bottom()

    plt.savefig(f'{"_".join(yvar1_list)}_and_{"_".join(yvar2_list)}_by_{xvar}{suffix}.png', dpi=400)

    if showplots:
        plt.show()

    plt.close()
    
    
def SaveScenarioPlot(ScenarioNO2predictions, ylimmin1 = 25,ylinmax1 = 300, ylimmin2 = 15,ylinmax2 = 35, showplots = False, suffix = ""):
    """This function saves a plot of the NO2 predictions for a set of simple traffic scenarios. The plot is a split y-axis plot with the traffic scenarios on the x-axis 
    and the NO2 values on the y-axis. There are lines for the maximum and mean NO2 values for all cells, the mean NO2 values for the cells on the road, 
    and the mean NO2 values for the cells neighboring the road (latter is optional). The function takes a ScenarioNO2predictions dataframe as input, which is the result of 
    the saveTraffScenarioNO2predictions function.

    Args:
        ScenarioNO2predictions (_type_): _description_
        ylimmin1 (int, optional): _description_. Defaults to 25.
        ylinmax1 (int, optional): _description_. Defaults to 300.
        ylimmin2 (int, optional): _description_. Defaults to 15.
        ylinmax2 (int, optional): _description_. Defaults to 35.
        showplots (bool, optional): _description_. Defaults to False.
        suffix (str, optional): _description_. Defaults to "".
    """
    
    colnames = ScenarioNO2predictions.columns
    if "ROAD_NEIGHBOR_MAX" in colnames:
        SplitYAxis2plusLineGraph(df = ScenarioNO2predictions, xvar="Scenarios",  yvar1_list = ["ScenarioMax", "ROAD_NEIGHBOR_MAX"], 
                         yvar2_list = ["ScenarioMeans", "ON_ROAD_MEAN", "ROAD_NEIGHBOR_MEAN"], yvarlabel1_list= ["Max All Cells", "Max Road Neighbor"],
                         yvarlabel2_list= ["Mean All Cells", "Mean On Road", "Mean Road Neighbor"], ylimmin1 = ylimmin1,ylinmax1 = ylinmax1,
                        ylimmin2 = ylimmin2,ylinmax2 = ylinmax2,  xlabel = "Traffic Scenarios: Factor of Status Quo Traffic Volume",
                        ylabel1 = "NO2 (µg/m3)", ylabel2 =  "NO2 (µg/m3)", showplots=showplots,  suffix=suffix)
    else:
        SplitYAxis2plusLineGraph(df = ScenarioNO2predictions, xvar="Scenarios",  yvar1_list = ["ScenarioMax"], 
                         yvar2_list = ["ScenarioMeans", "ON_ROAD_MEAN"], yvarlabel1_list= ["Max All Cells"],
                         yvarlabel2_list= ["Mean All Cells", "Mean On Road"], ylimmin1 = ylimmin1,ylinmax1 = ylinmax1,
                        ylimmin2 = ylimmin2,ylinmax2 = ylinmax2,  xlabel = "Traffic Scenarios: Factor of Status Quo Traffic Volume",
                        ylabel1 = "NO2 (µg/m3)", ylabel2 =  "NO2 (µg/m3)", showplots=showplots,  suffix=suffix)
        
        
def safeadjusterHistogram(adjuster, suffix = ""):
    """This function saves a histogram of the adjuster values to a png file. The adjuster is a list of values that are used for the morphological adjuster. 
    The histogram is saved to a file with the specified suffix.

    Args:
        adjuster (list(float)): A list of adjuster values.
        suffix (str, optional): A string extension to the filename (e.g. cellsize, matrixsize, any specification). Defaults to "".
    """
    plt.hist(adjuster, bins = 20, color = "#009999")
    plt.xlabel("Adjuster Values")
    plt.ylabel("Frequency")
    plt.title("Histogram of Adjuster Values")
    plt.savefig(f'AdjusterHistogram_{suffix}.png', dpi = 400)
    plt.close()
    
def meltPredictions(Predictions, stressor, cellsize):
    columnnames = [f"pred{stressor}_m{month}_h{hour}" for month in range(12) for hour in range(24)]
    Predictions_melted = pd.melt(Predictions, id_vars= ["int_id",  "baselineNO2"], value_vars=columnnames)
    Predictions_melted[["month", "hour"]] = Predictions_melted["variable"].str.extract(r'predNO2_m(\d+)_h(\d+)')
    Predictions_melted["NO2"] = Predictions_melted["value"]
    Predictions_melted["month"] = Predictions_melted["month"].astype(int)
    Predictions_melted["month"] += 1
    Predictions_melted["hour"] = Predictions_melted["hour"].astype(int)
    print(Predictions_melted.head())
    Predictions_melted.to_csv(f"{stressor}Predictions_melted_{cellsize}.csv", index=False)
    return Predictions_melted
    
def saveScenarioDescripts(Scenarios, cellsize, stressor, cellsubgroups = None):
    """This function saves summary statistics for the predictions for the different traffic 
    scenarios also per cell subgroup (e.g. ON_ROAD, ROAD_NEIGHBOR) in a csv file.

    Args:
        Scenarios (list(float)): A list of traffic scenario factor (status quo traffic times that factor)
        cellsize (str): The cell size of the grid
        stressor (str): The stressor for which the predictions are made (e.g. NO2)
        cellsubgroups (dataframe(int)): Optional. Defaults to None. A dataframe with the "int_id" and the different cell subgroups

    Returns:
        ScenarioPredictions (pd.DataFrame): A dataframe with the summary statistics for the predictions
    """
    ScenarioPredictions  = pd.DataFrame({"Scenarios": Scenarios, "Mean": np.nan, "Max": np.nan, "Min": np.nan})
    if cellsubgroups is not None:
        for celltype in cellsubgroups.columns[1:]:
            ScenarioPredictions[f"{celltype}_Mean"] = np.nan
            ScenarioPredictions[f"{celltype}_Max"] = np.nan
            ScenarioPredictions[f"{celltype}_Min"] = np.nan
    columnnames = [f"pred{stressor }_m{month}_h{hour}" for month in range(12) for hour in range(24)]
    for index, scenario in enumerate(Scenarios):   
        print("Loading Scenario: ", scenario)
        Pred = pd.read_csv(f"{stressor}predictions_{cellsize}_traffScenario_{scenario}.csv")
        Pred = Pred.merge(cellsubgroups, on="int_id", how="left")
        cellvals = Pred.loc[:, columnnames].values.flatten()
        ScenarioPredictions.loc[index, "Mean"] =  np.mean(cellvals)
        ScenarioPredictions.loc[index, "Max"] =  max(cellvals)
        ScenarioPredictions.loc[index, "Min"] =  min(cellvals)
        if cellsubgroups is not None:
            for celltype in cellsubgroups.columns[1:]:
                cellvals = Pred.loc[Pred[celltype] == 1, columnnames].values.flatten()
                ScenarioPredictions.loc[index, f"{celltype}_Mean"] =  np.mean(cellvals)
                ScenarioPredictions.loc[index, f"{celltype}_Max"] =  max(cellvals)
                ScenarioPredictions.loc[index, f"{celltype}_Min"] =  min(cellvals)
    ScenarioPredictions.to_csv(f"Scenario{stressor}predictions_{cellsize}.csv", index=False)
    return ScenarioPredictions
# CellAutDisp
This Python package provides functionalities for the dispersion modeling of traffic-related NO2 values. It includes functions for computing hourly and monthly dispersions, calibrating models, and running a genetic algorithm for calibration. Additionally, there are functions for applying the cellular automata dispersion model with various adjustments and coefficients.


## Table of Contents

- [Installation](#installation)
- [Usage](#usage)
- [Steps](#steps)
- [License](#license)

## Installation

The package can be installed using pip.
```bash
pip install CellAutDisp
```
## Usage
This instruction manual explains the steps and usage of functions for the purpose of traffic onroad to off road dispersion modeling. Selected important functions including their inputs are casted in italic for ease of identification. 


Broadly speaking the suggested order of steps are:
1. [Data Preparation](#data-preparation)
2. [Calibration](#calibration)
3. [Calibration Results Analysis](#calibresults)
4. [Scenario Analysis](#scenariomodeling)
5. [Integration of calibrated final model](#modelintegration)


Apart from the steps for preparing the CA-LUR model, there are core model components and functions that together make up the CA-LUR model.

**Dispersion Model Components**
   
   1. meteorology weighted moving window
  - *returnCorrectWeightedMatrix(meteolog, matrixsize, meteoparams, meteovalues)*<br>
      <sub> This function returns the correct weighted matrix based on the meteolog parameter. If set to True, the log of the meteorological values is taken apart from winddirection. It creates a matrix of weights based on meteorological parameters and wind direction. It takes the distance and degree vectors and calculates the  weight for each cell based on the distance and degree alignment as well as the meteorological factors.  The input meteoparams is a list of 9 parameters that need to be calibrated using the calibration module.<sub>
   
   2. morphology based adjuster
   - *provide_adjuster_flexible( morphparams, morphdata)*<br>
     <sub>This function calculates the adjustment factor for the dispersal kernel based on the morphological features and calibrated parameters (morphparams).  The morphparams is list of parameters that can be calibrated using the calibration module. The first three parameters are in that order (1) the intercept, (2) the maximum adjuster limit (3) the minimum adjuster limit. The remaining parameters are coefficients for the morphological features. The morphdata is dataframe with the morphological features (columns) for each cell (rows). The columns need to be ordered in the same way as the morphparams (from params 3 to how many you like). The morphparams and morphdata are flexible and can be used for any number of morphological features.<sub>

   3. cellular automata dispersion (different versions)

   - *compute_hourly_dispersion(raster, TrafficNO2, baselineNO2, onroadindices, weightmatrix, nr_repeats, adjuster = None, iter = True, baseline = False,  baseline_coeff = 1, traffemissioncoeff_onroad= 1,  traffemissioncoeff_offroad= 1)* <br> <sub>Computes the dispersion of the traffic NO2 values for one timestep (e.g. hour). The function uses the correct cellautom_dispersion function from the CA_dispersion module depending on the arguments: adjuster, iter and baseline.<sub>
     
     Below is a specification of the subfunctions from which it selects:

      - *cellautom_dispersion_dummy(weightmatrix, airpollraster, nr_repeats, baseline_NO2, onroadvalues)*<br>
        <sub>This function takes the weightmatrix, the airpollution raster, the number of iterations,the baseline NO2 values, the onroadvalues and applies the cellular automata dispersion model to the airpollution raster. This is the dummy version (the simplest version). It does not contain morphological adjustment factors nor scaling coefficients for the baseline and traffic estimations. It can be used with a meteorology weighted moving window, or a dummy equal weight window.<sub>
        
      - *cellautom_dispersion_adjust(weightmatrix, airpollraster, nr_repeats, adjuster, baseline_NO2, onroadvalues)*<br>
        <sub>This function takes the weightmatrix, the airpollution raster, the number of iterations, the baseline NO2 values, the onroadvalues, the morphological adjuster vector, and applies the cellular automata dispersion model to the airpollution raster. In this version the adjuster is applied a single time in the end.<sub>
        
      - *cellautom_dispersion_adjust_iter(weightmatrix, airpollraster, nr_repeats, adjuster, baseline_NO2, onroadvalues)*<br>
        <sub>This function takes the weightmatrix, the airpollution raster, the number of iterations, the baseline NO2 values, the onroadvalues, the morphological adjuster vector, and applies the cellular automata dispersion model to the airpollution raster. In this version the adjuster is applied in each iteration.<sub>
        
      - *cellautom_dispersion_adjust_scaled(weightmatrix, airpollraster, nr_repeats, adjuster, baseline_NO2, onroadvalues, baseline_coeff = 1, traffemissioncoeff_onroad = 1, traffemissioncoeff_offroad= 1)*<br>
        <sub>This function takes the weightmatrix, the airpollution raster, the number of iterations, the baseline NO2 values, the onroadvalues, the morphological adjuster vector, and the baseline and traffemission coefficients and applies the cellular automata dispersion model to the airpollution raster. In this version the adjuster is applied a single time in the end. The baseline and traffemission coefficients are applied in the end to scale the estimations.<sub>
        
      - *cellautom_dispersion_adjust_iter_scaled(weightmatrix, airpollraster, nr_repeats, adjuster, baseline_NO2, onroadvalues, baseline_coeff = 1, traffemissioncoeff_onroad = 1, traffemissioncoeff_offroad= 1)*<br>
        <sub>This function takes the weightmatrix, the airpollution raster, the number of iterations, the baseline NO2 values, the onroadvalues, the morphological adjuster vector, and the baseline and traffemission coefficients and applies the cellular automata dispersion model to the airpollution raster. In this version the adjuster is applied in each iteration. The baseline and traffemission coefficients are applied in the end to scale the estimations.<sub>


### Steps
1. **Data Preparation** <a id="data-preparation"></a>

      An example data preparation script can be found [here](https://github.com/TabeaSonnenschein/CellAutDisp/blob/main/ExampleApplications/01DataPreparationExample.py).

      1.1 Required Data:
      - baseline NO2
      - Traffic NO2 on roads
      - offroad measurement data for calibration (best also for external validation)
      - meteorological data
      - morphological data

      1.2 Data Processing:
      - *create_traffic_emission_columns(df, traff_coeff=np.nan,  TrI_coeff=np.nan, traffroadlength_coeff=np.nan, suffix="")*<br>
          <sub>Calculate traffic-related NO2 emissions based on traffic LUR coefficients and traffic data and the baseline NO2 and produce the Predictor Dataframe (Pred_df.csv) accordingly. The function also saves the Pred_df with the indicated suffix to a csv file.<sub>
          
      - *create_Eval_df(grid_sp, gridID, point_observations, observationsID, observations_colnames, desired_observation_colnames = None, suffix = "")*<br>
        <sub>This function takes a grid and point observations and returns a DataFrame with the observations joined to the grid. The function also saves the DataFrame (Eval_df) to a csv file.<sub>

      1.3 Initial Analytics:
      - *PrintSaveSummaryStats(df, dfname, suffix = "")*
      - *SingleVarViolinplot(df,variable, ylabel = None, filesuffix = None)*


2. **Calibration** <a id="calibration"></a>

      An example calibration script can be found [here](https://github.com/TabeaSonnenschein/CellAutDisp/blob/main/ExampleApplications/02CalibrationExample.py).

      Stepwise Calibration Process

      To justify and validate the structure of the model, we recommend a stepwise calibration process. In which model components are only added and specific settings selected if they improve the performance. The order of the stepwise calibration is:
      
          1. "meteomatrixsizerepeats", test meteolog = False and meteolog = True, and test different matrixsizes
          2. "morph", test iter = False and iter = True
          3. "meteonrrepeat"
          4. "scaling"
      
      For an example of such a calibration script see:

      Important Functions:
      - *makeFitnessfunction(calibtype, nr_cpus, matrixsize, raster, baselineNO2, TrafficNO2perhour, onroadindices, observations,  meteovalues_df, metric = "R2", uniqueparams = {},  moderator_df = None)* <br><sub>This function creates a fitness function for the calibration of the dispersion model. The fitness function is dependent on the calibration type and the metric. The calibration type can be one of "meteomatrixsizerepeats", "morph", "meteonrrepeat". The metric can be one of "R2", "RMSE". The uniqueparams argument should contain the parameters that are uniquely required for the calibration type. The moderator_df argument should be provided if the calibration type is "morph". The function returns two functions: the fitness function and the other performance function. The fitness function is the function that is minimized during calibration and is based on the specified metric. The other performance function is the function that is used to evaluate the performance of the model additionally after the calibration is complete.<sub>

      - *runGAalgorithm(fitnessfunction, param_settings, popsize, max_iter_noimprov, seed = None)* <br><sub>This function runs the genetic algorithm for the calibration of the dispersion model. The function returns the genetic algorithm object.<sub>

      - *PolishSaveGAresults(GAalgorithm, param_settings, fitnessfunction, otherperformancefunction, suffix)*<br><sub>This function polishes the results of the genetic algorithm and saves the results to csv files.<sub>

3. **Calibration Results Analysis**  <a id="calibresults"></a>

      An example Calibration result analysis script can be found [here](https://github.com/TabeaSonnenschein/CellAutDisp/blob/main/ExampleApplications/03CalibrationResultsAnalysisExample.py).
      - *saveMatrixPlotsPerMonth(matrixsize, meteoparams, meteovalues_df, meteolog = False, suffix = "", addMeteodata = False)*<br><sub>This function saves the weighted matrix plots for each month. The addMeteodata boolean parameter sets whether to add the meteorological data as text to the plot. it also adds and arrow to the plot to indicate the wind direction.<sub>

      - *jointMatrixVisualisation(figures_directory, matrixsize, suffix = "")* <br><sub>This function creates a combined figure of the weighted matrices for each month.<sub>

      - *saveNO2predictions(raster, TrafficNO2perhour, baselineNO2, onroadindices, matrixsize, meteoparams, repeatsparams, meteovalues_df, morphparams = None, scalingcoeffs = [1,1,1], moderator_df = None, iter = True, baseline = False, meteolog = False, suffix = "")*<br><sub> This function saves the NO2 predictions per hour and month to a csv file and print the summary statistics of the predictions. It will select the correct dispersion model based on the input parameters.<sub>
   
4. **Simple Scenario Modeling** <a id="scenariomodeling"></a>

      An example script for saving the predictions and scenario results can be found [here](https://github.com/TabeaSonnenschein/CellAutDisp/blob/main/ExampleApplications/04SavePredictionsExample.py), while a script for visualizing the results can be found [here](https://github.com/TabeaSonnenschein/CellAutDisp/blob/main/ExampleApplications/05PredictionAnalysisExample.py).

      - *saveTraffScenarioNO2predictions(trafficfactors, raster, TrafficNO2perhour, baselineNO2, onroadindices, matrixsize, meteoparams, repeatsparams, meteovalues_df, morphparams = None, scalingcoeffs = [1,1,1], moderator_df = None, iter = True, baseline = False, meteolog = False, suffix = "", roadneighborindices = None)*<br><sub> This function saves the NO2 predictions for a set of simple traffic scenarios to a csv file and prints the summary statistics of the predictions. The trafficscenarios are simple adjustments of the traffic and onroad NO2 by the specified factors. The trafficfactors parameters is that list of factors for the traffic scenarios. The function will select the correct dispersion model based on the input parameters.

      - *SaveScenarioPlot(ScenarioNO2predictions, ylimmin1 = 25,ylinmax1 = 300, ylimmin2 = 15,ylinmax2 = 35, showplots = False, suffix = "")*<br><sub> This function saves a plot of the NO2 predictions for a set of simple traffic scenarios. The plot is a split y-axis plot with the traffic scenarios on the x-axis and the NO2 values on the y-axis. There are lines for the maximum and mean NO2 values for all cells, the mean NO2 values for the cells on the road, and the mean NO2 values for the cells neighboring the road (latter is optional). The function takes a ScenarioNO2predictions dataframe as input, which is the result of the saveTraffScenarioNO2predictions function.<sub>

   
5. **Integration into other Models (e.g. more complex Scenario Models, Agent-based Models, ect.)** <a id="modelintegration"></a>

Since morphology is static, the adjuster vector can be calculated once using the morphology data and calibrated morphparams and then used throughout all interations of the model.

The meteorology-defined moving window varies per month and can be hence reused for estimations within a month. We offer the function .. to save the weightmatrix per months, so it can be simply loaded when needed. 

Finally the function

```
from CellAutDisp import compute_hourly_dispersion

result = compute_hourly_dispersion(argument1, argument2)
print(result)
```

## License
This project is licensed under the GNU General Public License - see the LICENSE.md file for details.

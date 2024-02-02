# CellAutDisp
This Python package provides functionalities for the dispersion modeling of traffic-related NO2 values. It includes functions for computing hourly and monthly dispersions, calibrating models, and running a genetic algorithm for calibration. Additionally, there are functions for applying the cellular automata dispersion model with various adjustments and coefficients.


## Table of Contents

- [Installation](#installation)
- [Usage](#usage)
- [Contributing](#contributing)
- [License](#license)

## Installation

Describe how to install your project. Include any dependencies that need to be installed, and provide code examples if necessary.

```bash
pip install CellAutDispers
```
## Usage

Functions including their inputs are casted in italic for ease of identification. This instruction manual explains the steps and usage of functions for the purpose of traffic onroad to off road dispersion modeling.

### Steps
1. **Data Preparation**
   
   1.1 Required Data:
   - baseline NO2
   - Traffic NO2 on roads
   - offroad measurement data for calibration (best also for external validation)
   - meteorological data
   - morphological data

   1.2 Data Processing:
   

   1.3 Initial Analytics:
   - *PrintSaveSummaryStats(df, dfname, suffix = "")*
   - *SingleVarViolinplot(df,variable, ylabel = None, filesuffix = None)*

2. **Dispersion Model Components**
   2.1 meteorology weighted moving window
    - *returnCorrectWeightedMatrix(meteolog, matrixsize, meteoparams, meteovalues)*: This function returns the correct weighted matrix based on the meteolog parameter. It creates a matrix of weights based on meteorological parameters and wind direction. It takes the distance and degree vectors and calculates the  weight for each cell based on the distance and degree alignment as well as the meteorological factors.  The input meteoparams is a list of 9 parameters that need to be calibrated using the calibration module.
   
   2.2 morphology based adjuster
   - *provide_adjuster_flexible( morphparams, morphdata)*: This function calculates the adjustment factor for the dispersal kernel based on the morphological features and calibrated parameters (morphparams).  The morphparams is list of parameters that can be calibrated using the calibration module. The first three parameters are in that order (1) the intercept, 
    (2) the maximum adjuster limit (3) the minimum adjuster limit. The remaining parameters are coefficients for the morphological features. The morphdata is dataframe 
    with the morphological features (columns) for each cell (rows). The columns need to be ordered in the same way as the morphparams (from params 3 to how many you like). The morphparams and morphdata are flexible and can be used for any number of morphological features.

   2.3 cellular automata dispersion (different versions)

- *compute_hourly_dispersion(raster, TrafficNO2, baselineNO2, onroadindices, weightmatrix, nr_repeats, adjuster = None, iter = True, baseline = False,  baseline_coeff = 1, traffemissioncoeff_onroad= 1,  traffemissioncoeff_offroad= 1)*: Computes the hourly dispersion of the traffic NO2 values for one timestep (e.g. hour). The function uses the correct cellautom_dispersion function from the CA_dispersion module depending on the arguments: adjuster, iter and baseline. Below are a specification of the subfunctions from which it selects.

      - *cellautom_dispersion_dummy(weightmatrix, airpollraster, nr_repeats, baseline_NO2, onroadvalues)*: This function takes the weightmatrix, the airpollution raster, the number of iterations,the baseline NO2 values, the onroadvalues and applies the cellular automata dispersion model to the airpollution raster. This is the dummy version (the simplest version). It does not contain morphological adjustment factors nor scaling coefficients for the baseline and traffic estimations. It can be used with a meteorology weighted moving window, or a dummy equal weight window.
      - *cellautom_dispersion_adjust(weightmatrix, airpollraster, nr_repeats, adjuster, baseline_NO2, onroadvalues)*: This function takes the weightmatrix, the airpollution raster, the number of iterations, the baseline NO2 values, the onroadvalues, the morphological adjuster vector, and applies the cellular automata dispersion model to the airpollution raster. In this version the adjuster is applied a single time in the end.
      - *cellautom_dispersion_adjust_iter(weightmatrix, airpollraster, nr_repeats, adjuster, baseline_NO2, onroadvalues)*: This function takes the weightmatrix, the airpollution raster, the number of iterations, the baseline NO2 values, the onroadvalues, the morphological adjuster vector, and applies the cellular automata dispersion model to the airpollution raster. In this version the adjuster is applied in each iteration.
      - *cellautom_dispersion_adjust_scaled(weightmatrix, airpollraster, nr_repeats, adjuster, baseline_NO2, onroadvalues, baseline_coeff = 1, traffemissioncoeff_onroad = 1, traffemissioncoeff_offroad= 1)*: This function takes the weightmatrix, the airpollution raster, the number of iterations, the baseline NO2 values, the onroadvalues, the morphological adjuster vector, and the baseline and traffemission coefficients and applies the cellular automata dispersion model to the airpollution raster. In this version the adjuster is applied a single time in the end. The baseline and traffemission coefficients are applied in the end to scale the estimations.
      - *cellautom_dispersion_adjust_iter_scaled(weightmatrix, airpollraster, nr_repeats, adjuster, baseline_NO2, onroadvalues, baseline_coeff = 1, traffemissioncoeff_onroad = 1, traffemissioncoeff_offroad= 1)*: This function takes the weightmatrix, the airpollution raster, the number of iterations, the baseline NO2 values, the onroadvalues, the morphological adjuster vector, and the baseline and traffemission coefficients and applies the cellular automata dispersion model to the airpollution raster. In this version the adjuster is applied in each iteration. The baseline and traffemission coefficients are applied in the end to scale the estimations.


3. **Calibration**
   5.1 Stepwise Calibration Process

   5.2 Results Analytics
   - *saveMatrixPlotsPerMonth(matrixsize, meteoparams, meteovalues_df, meteolog = False, suffix = "", addMeteodata = False)*: This function saves the weighted matrix plots for each month. The addMeteodata boolean parameter sets whether to add the meteorological data as text to the plot. it also adds and arrow to the plot to indicate the wind direction.


4. **Simple Scenario Modeling**
   
5. **Integration into Models (e.g. more complex Scenario Models, Agent-based Models, ect.)** 


```from your_package_name import your_function

result = your_function(argument1, argument2)
print(result)
```

## License
This project is licensed under the MIT License - see the LICENSE.md file for details.

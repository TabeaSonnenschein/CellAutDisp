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

3. **Dispersion Model Components**
   2.1 meteorology weighted moving window
    - *returnCorrectWeightedMatrix(meteolog, matrixsize, meteoparams, meteovalues)*: This function returns the correct weighted matrix based on the meteolog parameter. It creates a matrix of weights based on meteorological parameters and wind direction. It takes the distance and degree vectors and calculates the  weight for each cell based on the distance and degree alignment as well as the meteorological factors.  The input meteoparams is a list of 9 parameters that need to be calibrated using the calibration module.
   
   2.2 morphology based adjuster
   - 

   2.3 cellular automata dispersion


5. **Calibration**
   5.1 Stepwise Calibration Process

   5.2 Results Analytics
   - *saveMatrixPlotsPerMonth(matrixsize, meteoparams, meteovalues_df, meteolog = False, suffix = "", addMeteodata = False)*: This function saves the weighted matrix plots for each month. The addMeteodata boolean parameter sets whether to add the meteorological data as text to the plot. it also adds and arrow to the plot to indicate the wind direction.


7. Application (e.g. Scenario Modeling)
8. Integration into Models


```from your_package_name import your_function

result = your_function(argument1, argument2)
print(result)
```

## License
This project is licensed under the MIT License - see the LICENSE.md file for details.

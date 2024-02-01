import numpy as np
from xrspatial  import focal
from xrspatial.utils import ngjit

def set_onroadvalues(airpollraster, onroadvalues, newvals = None):
    """This function takes a raster and a dataframe with onroadvalues 
    and sets the onroadvalues in the raster to the values in the dataframe.

    Args:
        airpollraster (raster(float)): the raster with the airpollution values
        onroadvalues (df(float, int)): a dataframe with the onroadvalues and the corresponding cell ids

    Returns:
        raster(float): returns the updated raster with the onroadvalues
    """
    if newvals is None:
        newvals = (np.asarray(airpollraster[:]).flatten())
    newvals[onroadvalues["int_id"]] = onroadvalues.iloc[:,1]
    airpollraster[:] = np.array(newvals).reshape(airpollraster.shape)
    return airpollraster

    
def apply_adjuster(airpollraster, adjuster):
    """The function takes the airpollution raster and 
    the adjuster vector and applies the adjuster to the airpollution raster.

    Args:
        airpollraster (raster(float)): the raster with the airpollution values
        adjuster (list(float)): A list of morphological adjustment factors for each cell

    Returns:
        list(float): a list with the adjusted airpollution values
    """
    return (np.asarray(airpollraster[:]).flatten() + (np.asarray(airpollraster[:]).flatten() * adjuster))


def apply_traffemission_coeffs(newvals, onroadvalues, traffemissioncoeff1, traffemissioncoeff2):
    """_summary_

    Args:
        newvals (list(float)): a list with the adjusted airpollution values
        onroadvalues (df(float, int)): a dataframe with the onroadvalues and the corresponding cell ids
        traffemissioncoeff_onroad (float): a calibration parameter for scaling the onroad emissions
        traffemissioncoeff_offroad (float): a calibration parameter for scaling the offroad emissions

    Returns:
        _type_: _description_
    """
    newvals[onroadvalues["int_id"]] = newvals[onroadvalues["int_id"]]*traffemissioncoeff1
    newvals[~np.isin(np.arange(len(newvals)), onroadvalues["int_id"])] = newvals[~np.isin(np.arange(len(newvals)), onroadvalues["int_id"])]*traffemissioncoeff2
    return newvals


def create_weightedaverage_function(weightmatrix):
    """This function takes a weightmatrix and returns a function that calculates the weighted average of a kernel.

    Args:
        weightmatrix (matrix(float)): the meteorologically defined weight matrix

    Returns:
        function: a function that calculates the weighted average of a kernel using the weightmatrix
    """
    @ngjit    
    def weightedaverage(kernel_data):
       if np.nansum(weightmatrix) == 0:
           return 0
       else:
           return round((np.nansum(np.multiply(kernel_data, weightmatrix))/np.nansum(weightmatrix)),10)
    return weightedaverage


def cellautom_dispersion_dummy(weightmatrix, airpollraster, nr_repeats, baseline_NO2, onroadvalues):
    """This function takes the weightmatrix, the airpollution raster, 
    the number of iterations,the baseline NO2 values, the onroadvalues 
    and applies the cellular automata dispersion model to the airpollution raster. 
    This is the dummy version (the simplest version). 
    It does not contain morphological adjustment factors nor
    scaling coefficients for the baseline and traffic estimations.
    
    Args:
        weightmatrix (matrix(float)): the meteorologically defined weight matrix
        airpollraster (raster(float)): the raster with the initial traffic induced air pollution values
        nr_repeats (int): the calibrated number of iterations
        baseline_NO2 (list(float)): a list of the baseline NO2 values for each cell
        onroadvalues (df(float, int)): a dataframe with the onroadvalues and the corresponding cell ids

    Returns:
        list(float): a list of the estimations of the airpollution values for each cell
    """  
    weightedaverage = create_weightedaverage_function(weightmatrix)
    for _ in range(int(nr_repeats)):
            airpollraster = set_onroadvalues(airpollraster, onroadvalues)
            airpollraster[:] =  focal.apply(raster = airpollraster, kernel= np.full(weightmatrix.shape, 1), func= weightedaverage)
    return (np.asarray(airpollraster[:]).flatten()) + (baseline_NO2)


def cellautom_dispersion_adjust(weightmatrix, airpollraster, nr_repeats, adjuster, baseline_NO2, onroadvalues):
    """This function takes the weightmatrix, the airpollution raster, 
    the number of iterations, the baseline NO2 values, the onroadvalues, 
    the morphological adjuster vector, and applies the cellular automata 
    dispersion model to the airpollution raster.  In this version the adjuster 
    is applied a single time in the end.

    Args:
        weightmatrix (matrix(float)): the meteorologically defined weight matrix
        airpollraster (raster(float)): the raster with the initial traffic induced air pollution values
        nr_repeats (int): the calibrated number of iterations
        adjuster (list(float)): A list of morphological adjustment factors for each cell
        baseline_NO2 (list(float)): a list of the baseline NO2 values for each cell
        onroadvalues (df(float, int)): a dataframe with the onroadvalues and the corresponding cell ids

    Returns:
        list(float): a list of the estimations of the airpollution values for each cell
    """  
    weightedaverage = create_weightedaverage_function(weightmatrix)
    for i in range(int(nr_repeats)):
            airpollraster = set_onroadvalues(airpollraster, onroadvalues)
            airpollraster[:] =  focal.apply(raster = airpollraster, kernel=np.full(weightmatrix.shape, 1), func= weightedaverage)
    newvals = apply_adjuster(airpollraster, adjuster)
    return newvals + baseline_NO2

def cellautom_dispersion_adjust_iter(weightmatrix, airpollraster, nr_repeats, adjuster, baseline_NO2, onroadvalues):
    """This function takes the weightmatrix, the airpollution raster, 
    the number of iterations, the baseline NO2 values, the onroadvalues, 
    the morphological adjuster vector, and applies the cellular automata 
    dispersion model to the airpollution raster. In this version the adjuster 
    is applied in each iteration.

    Args:
        weightmatrix (matrix(float)): the meteorologically defined weight matrix
        airpollraster (raster(float)): the raster with the initial traffic induced air pollution values
        nr_repeats (int): the calibrated number of iterations
        adjuster (list(float)): A list of morphological adjustment factors for each cell
        baseline_NO2 (list(float)): a list of the baseline NO2 values for each cell
        onroadvalues (df(float, int)): a dataframe with the onroadvalues and the corresponding cell ids

    Returns:
        list(float): a list of the estimations of the airpollution values for each cell
    """  
    weightedaverage = create_weightedaverage_function(weightmatrix)
    newvals = np.asarray(airpollraster[:]).flatten() 
    for _ in range(int(nr_repeats)):
            airpollraster = set_onroadvalues(airpollraster, onroadvalues, newvals = newvals)
            airpollraster[:] =  focal.apply(raster = airpollraster, kernel= np.full(weightmatrix.shape, 1), func= weightedaverage)
            newvals = apply_adjuster(airpollraster, adjuster)
    return newvals + baseline_NO2


def cellautom_dispersion_adjust_scaled(weightmatrix, airpollraster, nr_repeats, adjuster, 
                                       baseline_NO2, onroadvalues, baseline_coeff = 1, 
                                       traffemissioncoeff_onroad = 1, traffemissioncoeff_offroad= 1):
    """This function takes the weightmatrix, the airpollution raster, 
    the number of iterations, the baseline NO2 values, the onroadvalues, 
    the morphological adjuster vector, and the baseline and traffemission coefficients
    and applies the cellular automata dispersion model to the airpollution raster. 
    In this version the adjuster is applied a single time in the end. 
    The baseline and traffemission coefficients are applied in the end to scale the estimations.

    Args:
        weightmatrix (matrix(float)): the meteorologically defined weight matrix
        airpollraster (raster(float)): the raster with the initial traffic induced air pollution values
        nr_repeats (int): the calibrated number of iterations
        adjuster (list(float)): A list of morphological adjustment factors for each cell
        baseline_NO2 (list(float)): a list of the baseline NO2 values for each cell
        onroadvalues (df(float, int)): a dataframe with the onroadvalues and the corresponding cell ids
        baseline_coeff (int, optional): a calibrated parameter for scaling the baseline NO2. Defaults to 1.
        traffemissioncoeff_onroad (float): a calibration parameter for scaling the onroad emissions. Defaults to 1.
        traffemissioncoeff_offroad (float): a calibration parameter for scaling the offroad emissions.Defaults to 1.

    Returns:
        list(float): a list of the estimations of the airpollution values for each cell
    """   
    weightedaverage = create_weightedaverage_function(weightmatrix)
    for _ in range(int(nr_repeats)):
           airpollraster= set_onroadvalues(airpollraster, onroadvalues)
           airpollraster[:] =  focal.apply(raster = airpollraster, kernel= np.full(weightmatrix.shape, 1), func= weightedaverage)
    newvals = apply_adjuster(airpollraster, adjuster)
    newvals = apply_traffemission_coeffs(newvals, onroadvalues, traffemissioncoeff_onroad, traffemissioncoeff_offroad)
    return newvals + (baseline_NO2*baseline_coeff)


def cellautom_dispersion_adjust_iter_scaled(weightmatrix, airpollraster, nr_repeats, adjuster, 
                                            baseline_NO2, onroadvalues, baseline_coeff = 1, 
                                            traffemissioncoeff_onroad = 1, traffemissioncoeff_offroad= 1):
        
    """This function takes the weightmatrix, the airpollution raster, 
    the number of iterations, the baseline NO2 values, the onroadvalues, 
    the morphological adjuster vector, and the baseline and traffemission coefficients
    and applies the cellular automata dispersion model to the airpollution raster. 
    In this version the adjuster is applied in each iteration. 
    The baseline and traffemission coefficients are applied in the end to scale the estimations.

    Args:
        weightmatrix (matrix(float)): the meteorologically defined weight matrix
        airpollraster (raster(float)): the raster with the initial traffic induced air pollution values
        nr_repeats (int): the calibrated number of iterations
        adjuster (list(float)): A list of morphological adjustment factors for each cell
        baseline_NO2 (list(float)): a list of the baseline NO2 values for each cell
        onroadvalues (df(float, int)): a dataframe with the onroadvalues and the corresponding cell ids
        baseline_coeff (int, optional): a calibrated parameter for scaling the baseline NO2. Defaults to 1.
        traffemissioncoeff_onroad (float): a calibration parameter for scaling the onroad emissions. Defaults to 1.
        traffemissioncoeff_offroad (float): a calibration parameter for scaling the offroad emissions.Defaults to 1.

    Returns:
        list(float): a list of the estimations of the airpollution values for each cell
    """  
    weightedaverage = create_weightedaverage_function(weightmatrix)
    newvals = np.asarray(airpollraster[:]).flatten() 
    for _ in range(int(nr_repeats)):
            airpollraster = set_onroadvalues(airpollraster, onroadvalues, newvals = newvals)
            airpollraster[:] =  focal.apply(raster = airpollraster, kernel= np.full(weightmatrix.shape, 1), func= weightedaverage)
            newvals = apply_adjuster(airpollraster, adjuster)
    newvals = apply_traffemission_coeffs(newvals, onroadvalues, traffemissioncoeff_onroad, traffemissioncoeff_offroad)
    return newvals + (baseline_NO2*baseline_coeff)


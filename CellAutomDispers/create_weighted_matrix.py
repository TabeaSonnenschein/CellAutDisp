import numpy as np
from math import log
import matplotlib.pyplot as plt

def create_matrix_and_calculate_vectors(matrixsize):
    """ Create an matrixsize x matrixsize matrix and calculate the relative 
    distance and degree vectors for each cell.
    Args:
        matrixsize (int): matrix size. Must be odd.

    Returns:
        matrix, list, list: the matrix, the distance vector, the degree vector
    """
    # Create an matrixsize x matrixsize matrix
    matrix = np.zeros((matrixsize, matrixsize))

    # Calculate the center coordinates
    center_x, center_y = matrixsize // 2, matrixsize // 2

    # Initialize matrices to store relative coordinates, distances, and degrees
    distances, degrees = matrix.copy(), matrix.copy()

    # Iterate through each cell in the matrix
    for i in range(matrixsize):
        for j in range(matrixsize):
            # Calculate relative vector coordinates
            relative_x, relative_y = i - center_x, j - center_y

            # distance = np.linalg.norm([relative_x, relative_y]) # Euclidean norm vector distance
            distance = max(abs(relative_x), abs(relative_y)) #Chebyshev Distance
            distances[i, j] = distance

            # # Calculate the degree of the vector from the cell to the center
            angle_rad = np.arctan2(relative_y, -relative_x)  # Negate relative_y for clockwise direction
            degree = np.degrees(angle_rad)
            
            # Adjust negative angles to cover the full 360 degrees
            degree = (degree + 360) % 360

            # Store the results in the matrix
            degrees[i, j] = degree

    return matrix, distances, degrees


def continuous_meteo_matrix(matrixsize, meteoparams, temperature, rain, windspeed, winddirection):
    """ This function creates a matrix of weights based on meteorological parameters and wind direction.
    It takes the distance and degree vectors and calculates the 
    weight for each cell based on the distance and degree alignment as well as the meteorological factors.
    The input meteoparams is a list of 9 parameters that need to be calibrated using the calibration module.

    Args:
        matrixsize (int): the matrix size. Must be odd.
        meteoparams (list(float)): parameterlist from the calibration module
        temperature (float): one observation of temperature (Celsius degrees)
        rain (float): one observation of rain (mm)
        windspeed (float): one observation of windspeed (m/s)
        winddirection (float): one observation of winddirection (degrees)

    Raises:
        ValueError: if matrixsize is not odd
        
    Returns:
        matrix(float): the weight matrix
    """
    # check if n is odd
    if matrixsize % 2 == 0:
        raise ValueError("matrixsize must be odd")
    
    # calculate meteorological influence
    baseW = meteoparams[0] + (meteoparams[1] * temperature) + (meteoparams[2] * rain) + (meteoparams[3] * windspeed)
    if baseW < 0:
        baseW = 0
    disparity_factor = meteoparams[4] + (meteoparams[5] * windspeed)
    
    #create matrix and distances and degree vectors
    weight_matrix, distances, degrees = create_matrix_and_calculate_vectors(matrixsize)
    degree_alignment = abs(degrees - winddirection)
    
    # adjust the baseW based on distance and degree alignment
    baseW_dist_degree = baseW*((meteoparams[6]*(1 / (distances+0.01))) + (meteoparams[7]*(1/(degree_alignment + 1)))) #the further away the less the effect, the further from wind direction the less the effect
        
    # incorporate windspeed disparity factor
    weight_matrix[np.where(degree_alignment <= 90)] = baseW_dist_degree[np.where(degree_alignment <= 90)] * disparity_factor #windward
    weight_matrix[np.where(degree_alignment > 90)] = baseW_dist_degree[np.where(degree_alignment > 90)] /disparity_factor #leeward
    
    #inertia
    weight_matrix[matrixsize // 2, matrixsize // 2] = meteoparams[8] / disparity_factor #the more wind the less inertia
    return weight_matrix

def continuous_meteo_matrix_log(matrixsize, meteoparams, temperature, rain, windspeed, winddirection):
    """ This function creates a matrix of weights based on meteorological parameters and wind direction.
    It takes the distance and degree vectors and calculates the
    weight for each cell based on the distance and degree alignment as well as the meteorological factors.
    The input meteoparams is a list of 9 parameters that need to be calibrated using the calibration module.
    This version takes the log of the meteorological values apart from winddirection.
    
    Args:
        matrixsize (int): the matrix size. Must be odd.
        meteoparams (list(float)): parameterlist from the calibration module
        temperature (float): one observation of temperature (Celsius degrees)
        rain (float): one observation of rain (mm)
        windspeed (float): one observation of windspeed (m/s)
        winddirection (float): one observation of winddirection (degrees)

    Raises:
        ValueError: if n is not odd
        
    Returns:
        matrix(float): the weight matrix
    """
    return continuous_meteo_matrix(matrixsize, meteoparams, log(temperature), log(rain), log(windspeed), winddirection)

def returnCorrectWeightedMatrix(meteolog, matrixsize, meteoparams, meteovalues):
    """This function returns the correct weighted matrix based on the meteolog parameter.

    Args:
        meteolog (Boolean): if True, the log of the meteorological values is taken apart from winddirection
        matrixsize (int): An odd integer that determines the size of the matrix
        meteoparams (list(float)): parameterlist from the calibration module
        meteovalues (list(float)): a list of meteorological values order as: temperature, rain, windspeed, winddirection

    Returns:
        matrix(float): the weight matrix
    """
    if meteolog:
        return continuous_meteo_matrix_log(matrixsize, meteoparams= meteoparams, 
                                                   temperature= meteovalues[0], rain = meteovalues[1],
                                                   windspeed = meteovalues[2], winddirection = meteovalues[3])
    else:
        return continuous_meteo_matrix(matrixsize, meteoparams= meteoparams, 
                                                   temperature= meteovalues[0], rain = meteovalues[1],
                                                   windspeed = meteovalues[2], winddirection = meteovalues[3])

def plotWeightedMatrix(matrixsize, meteoparams, meteovalues, meteolog, suffix = "", show = False):
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
    plt.savefig(f"weighted_matrix{suffix}.png")
    if show:
        plt.show()
    plt.close()
        
def saveMatrixPlotsPerMonth(matrixsize, meteoparams, meteovalues_df, meteolog = False, suffix = ""):
    """This function saves the weighted matrix plots for each month.

    Args:
        matrixsize (int): An odd integer that determines the size of the matrix
        meteoparams (list(float)): parameterlist from the calibration module
        meteovalues_df (dataframe(float)): A dataframe of all meteorological values for each month (months are rows). The dataframe should have the columns "Temperature", "Rain", "Windspeed", "Winddirection" in that order.
        meteolog (Boolean): if True, the log of the meteorological values is taken apart from winddirection

    """
    for month in range(12):
        meteovalues = meteovalues_df.iloc[month].values
        plotWeightedMatrix(matrixsize, meteoparams, meteovalues, meteolog, suffix = f"MS{matrixsize}_M{month+1}{suffix}", show = False)
    
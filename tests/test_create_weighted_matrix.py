import numpy as np
import pytest
import sys
sys.path.append(r'C:\Users\Tabea\Documents\GitHub\CellAutomDispers')
from CellAutomDispers.create_weighted_matrix import continuous_meteo_matrix, plotWeightedMatrix
import matplotlib.pyplot as plt

def test_continuous_meteo_matrix():
    # Test parameters
    matrixsize = 5
    # meteoparams = [1, 2, 3, 4, 5, 6, 7, 8, 9]
    # meteoparams = [0.409801,  0.011337,  0.162194, -0.096162,  0.674607,  0.830106,  0.304844,  0.077549,  4.926544]
    meteoparams = [0.207138688, 0.846322669, 1.481799657, 1.347646565, 1.838088435, 0.126466865, 1.113600211, 0.171088088, 3.193482071]

    temperature = 25.0  # Celsius degrees
    rain = 10.0  # mm
    windspeed = 10.0  # m/s
    winddirection = 180.0  # degrees

    # Ensure n is odd
    with pytest.raises(ValueError, match="matrixsize must be odd"):
        continuous_meteo_matrix(4, meteoparams, temperature, rain, windspeed, winddirection)

    # Test the function
    weight_matrix = continuous_meteo_matrix(matrixsize, meteoparams, temperature, rain, windspeed, winddirection)
    print(weight_matrix)
    
    # Check the shape of the weight matrix
    assert weight_matrix.shape == (matrixsize, matrixsize)

    # Check that the center cell has the correct value (inertia)
    assert weight_matrix[matrixsize // 2, matrixsize // 2] == pytest.approx(meteoparams[8] / (meteoparams[4] + (meteoparams[5] * windspeed)))

    # Check that all values in the weight matrix are greater than or equal to 0
    assert (weight_matrix >= 0).all()

    # Check that the weight matrix is symmetric,it needs to be symmetric on a vertical axis, 
    # since the test wind direction is 180 degrees
    assert np.allclose(weight_matrix, weight_matrix[:, ::-1])

    # show a plot of the weight matrix
    plt.imshow(weight_matrix)
    # add a colorbar
    plt.colorbar()
    plt.show()



# You can run the tests using the following command in the terminal:
# pytest test_create_weighted_matrix.py
print(test_continuous_meteo_matrix())
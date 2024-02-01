import numpy as np
import pandas as pd
import pytest
from CellAutomDispers.provide_adjuster import provide_adjuster

def test_provide_adjuster():
    # Test parameters
    morph_params = [1, 2, 3, 4, 5, 6, 7, 8]
    green_cover = pd.Series([0.2, 0.4, 0.6, 0.8])
    open_space_fraction = pd.Series([0.1, 0.3, 0.5, 0.7])
    nr_trees = pd.Series([10, 20, 30, 40])
    building_height = pd.Series([5.0, 10.0, 15.0, 20.0])
    neigh_height_diff = pd.Series([2.0, 4.0, 6.0, 8.0])

    # Test the function
    adjuster = provide_adjuster(morph_params, green_cover, open_space_fraction, nr_trees, building_height, neigh_height_diff)

    # Check the length of the adjuster list
    assert len(adjuster) == len(green_cover)

    # Check that the adjuster values are within the specified range
    assert (morph_params[7] <= adjuster).all() and (adjuster <= morph_params[6]).all()

    # Check specific values based on your expected behavior
    # Add more assertions based on your specific expectations and test cases
    # ...

# You can run the tests using the following command in the terminal:
# pytest test_your_module_name.py
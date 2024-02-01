import numpy as np
import pytest
import CellAutomDispers
from CellAutomDispers.performance_metrics import compute_R, compute_MSE, compute_Errors, compute_all_metrics

def test_compute_R():
    # Test parameters
    pred = np.array([1.0, 2.0, 3.0, 4.0])
    obs = np.array([1.1, 2.2, 3.3, 4.4])

    # Test the function
    correlation_coefficient = compute_R(pred, obs)

    # Check the result
    assert correlation_coefficient == pytest.approx(1.0)  # Adjust this based on your expected output

def test_compute_MSE():
    # Test parameters
    pred = np.array([1.0, 2.0, 3.0, 4.0])
    obs = np.array([1.1, 2.2, 3.3, 4.4])

    # Test the function
    mse = compute_MSE(pred, obs)

    # Check the result
    assert mse == pytest.approx(0.01)  # Adjust this based on your expected output

def test_compute_Errors():
    # Test parameters
    pred = np.array([1.0, 2.0, 3.0, 4.0])
    obs = np.array([1.1, 2.2, 3.3, 4.4])

    # Test the function
    mse, mae, me = compute_Errors(pred, obs)

    # Check the results
    assert mse == pytest.approx(0.01)  # Adjust this based on your expected output
    assert mae == pytest.approx(0.1)   # Adjust this based on your expected output
    assert me == pytest.approx(0.025)   # Adjust this based on your expected output

def test_compute_all_metrics():
    # Test parameters
    pred = np.array([1.0, 2.0, 3.0, 4.0])
    obs = np.array([1.1, 2.2, 3.3, 4.4])

    # Test the function
    r, mse, mae, me = compute_all_metrics(pred, obs)

    # Check the results
    assert r == pytest.approx(1.0)  # Adjust this based on your expected output
    assert mse == pytest.approx(0.01)  # Adjust this based on your expected output
    assert mae == pytest.approx(0.1)   # Adjust this based on your expected output
    assert me == pytest.approx(0.025)   # Adjust this based on your expected output

# Run the tests using the following command in the terminal:
# pytest test_performance_metrics.py
from scipy.stats import pearsonr
from sklearn.metrics import mean_squared_error, mean_absolute_error
import numpy as np
from math import sqrt


def compute_R(pred, obs):
    """This function return the Pearson correlation coefficient between two arrays.

    Args:
        pred (list(float)): the predicted values
        obs (list(float)): the observed values

    Returns:
        float: the Pearson correlation coefficient
    """
    if any(np.isinf(pred)):
        return 0
    else:
        diff = obs - pred
        r, _ = pearsonr(pred[~np.isnan(diff)], obs[~np.isnan(diff)])
        return r
    
def compute_MSE(pred, obs):
    """This function return the mean squared error between two arrays.

    Args:
        pred (list(float)): the predicted values
        obs (list(float)): the observed values

    Returns:
        float: the mean squared error
    """
    diff = obs - pred
    return mean_squared_error(obs[~np.isnan(diff)],pred[~np.isnan(diff)])

def compute_Errors(pred, obs):
    """Computes the mean squared error, mean average error and mean error between two arrays.

    Args:
        pred (list(float)): the predicted values
        obs (list(float)): the observed values

    Returns:
        float, float, float:  mean squared error, mean average error and mean error
    """
    diff = obs - pred    
    # Mean squared error
    MSE = mean_squared_error(obs[~np.isnan(diff)],pred[~np.isnan(diff)])
    # Mean absolute error
    MAE = mean_absolute_error(obs[~np.isnan(diff)],pred[~np.isnan(diff)])
    # Mean error
    ME = (pred[~np.isnan(diff)]-obs[~np.isnan(diff)]).mean()
    return MSE, MAE, ME

def compute_all_metrics(pred, obs):
    """Computes the Pearson correlation coefficient, mean squared error, 
        mean average error and mean error between two arrays

    Args:
        pred (list(float)): the predicted values
        obs (list(float)): the observed values

    Returns:
        float,float, float, float:  Pearson correlation coefficient, mean squared error, mean average error and mean error
    """
    r = compute_R(pred, obs)
    MSE, MAE, ME = compute_Errors(pred, obs)
    return r, MSE, MAE, ME

def compute_Metric(pred, obs, metric = "R2"):
    """Returns the metric between two arrays

    Args:
        pred (list(float)): the predicted values
        obs (list(float)): the observed values
        metric (str, optional): the metric to compute. Defaults to "R".

    Returns:
        float: the metric between the two arrays
    """
    if metric == "R2":
        return compute_R(pred, obs)
    elif metric == "MSE":
        return compute_MSE(pred, obs)
    elif metric == "Errors":
        return compute_Errors(pred, obs)
    else:
        return compute_all_metrics(pred, obs)
    
def print_Errors(MSE, MAE, ME, prefix = ""):
    """Prints the mean squared error, mean average error and mean error

    Args:
        MSE (float): The Mean Squared Error, will be used to print the Root Mean Squared Error
        MAE (float): The Mean Average Error
        ME (float): The Mean Error
        prefix (str, optional): A Prefix that will be added in front of the print. Defaults to "".
    """
    print(f"{prefix} RMSE: {sqrt(MSE)}") 
    print(f"{prefix} MAE: {MAE}")
    print(f"{prefix} ME: {ME}")
    
def print_R2(r, prefix = ""):
    """Prints the R2 based on the Pearson correlation coefficient to the power of 2.
    
    Args:
        r (float): The Pearson correlation coefficient
        prefix (str, optional): A Prefix that will be added in front of the print. Defaults to "".
    """
    if r != 0:
        print(f"{prefix} R2: {r**2}") 
    else:
        print(f"{prefix} R2: {r}")
    
def print_all_metrics(r, MSE, MAE, ME, prefix = ""):
    """Prints the R2 based on the Pearson correlation coefficient to the power of 2,
        the root mean squared error, mean average error and mean error

    Args:
        r (float): The Pearson correlation coefficient
        MSE (float): The Mean Squared Error, will be used to print the Root Mean Squared Error
        MAE (float): The Mean Average Error
        ME (float): The Mean Error
        prefix (str, optional): A Prefix that will be added in front of the print. Defaults to "".
    """
    print(f"{prefix} R2: {r**2}")
    print_Errors(MSE, MAE, ME, prefix = prefix)
    
def print_RMSE(MSE, prefix = ""):
    """Prints the root mean squared error based on the mean squared error.
        
    Args:
        MSE (float): The Mean Squared Error, will be used to print the Root Mean Squared Error
        prefix (str, optional): A Prefix that will be added in front of the print. Defaults to "".
    """
    print(f"{prefix} RMSE: {sqrt(MSE)}")
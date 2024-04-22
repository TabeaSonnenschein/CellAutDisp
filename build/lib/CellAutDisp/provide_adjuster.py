def provide_adjuster(morphparams, GreenCover, openspace_fraction, NrTrees, 
                     building_height, neigh_height_diff ):
    """This function calculates the adjustment factor for the dispersal kernel 
    based on the morphological features and calibrated parameters (morphparams).

    Args:
        morphparams (list(float)): a list of 7 parameters that need to be calibrated using the calibration module
        GreenCover (list(float)): A list of green cover values for each cell
        openspace_fraction (list(float)): A list of open space fraction values for each cell
        NrTrees (list(int)): A list of number of trees values for each cell
        building_height (list(float)): A list of building height values for each cell
        neigh_height_diff (list(float)): A list of height difference to the neighbour values for each cell

    Returns:
        list(float): A list of adjustment factors for each cell
    """
    adjuster = (morphparams[0] + (morphparams[1] * GreenCover.fillna(0)) + (morphparams[2] * openspace_fraction.fillna(0)) +
                       (morphparams[3] * NrTrees.fillna(0)) + (morphparams[4] * building_height.fillna(0)) + 
                       (morphparams[5] * neigh_height_diff.fillna(0)))
    adjuster[adjuster > morphparams[6]] = morphparams[6]
    adjuster[adjuster < morphparams[7]] = morphparams[7]
    return adjuster

def provide_adjuster_flexible( morphparams, morphdata):
    """This function calculates the adjustment factor for the dispersal kernel 
    based on the morphological features and calibrated parameters (morphparams). 
    The morphparams a list of parameters that need to be calibrated using the calibration module. 
    The first three parameters are in that order (1) the intercept, 
    (2) the maximum adjuster limit (3) the minimum adjuster limit. 
    The remaining parameters are coefficients for the morphological features. The morphdata is dataframe 
    with the morphological features (columns) for each cell (rows). The columns need to be ordered in 
    the same way as the morphparams (from params 3 to how many you like)
    The morphparams and morphdata are flexible and can be used for any number of morphological features.

    Args:
        morphparams (list(float)): a list of parameters that need to be calibrated using the calibration module. The first three parameters are in that order (1) the intercept, (2) the maximum adjuster limit (3) the minimum adjuster limit. The remaining parameters are coefficients for the morphological features.
        morphdata (dataframe(float)): A dataframe with the morphological features (columns) for each cell (rows). The columns need to be ordered in the same way as the morphparams (from params 3 to how many you like).

    Returns:
        list(float): A list of adjustment factors for each cell
    """
    adjuster = morphparams[0] + (morphdata * morphparams[3:]).sum(axis=1)
    adjuster[adjuster > morphparams[1]] = morphparams[1]
    adjuster[adjuster < morphparams[2]] = morphparams[2]
    return adjuster
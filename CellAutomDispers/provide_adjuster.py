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
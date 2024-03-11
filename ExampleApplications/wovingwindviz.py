import numpy as np
from math import log
import matplotlib.pyplot as plt
import os
import matplotlib.patches as patches
import math 

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

            distance = np.linalg.norm([relative_x, relative_y]) # Euclidean norm vector distance
            # distance = max(abs(relative_x), abs(relative_y)) #Chebyshev Distance
            distances[i, j] = distance

            # # Calculate the degree of the vector from the cell to the center
            angle_rad = np.arctan2(relative_y, -relative_x)  # Negate relative_y for clockwise direction
            degree = np.degrees(angle_rad)
            
            # Adjust negative angles to cover the full 360 degrees
            degree = (degree + 360) % 360

            # Store the results in the matrix
            degrees[i, j] = degree

    return matrix, distances, degrees

def get_text_colordegrees(value):
    # Returns 'black' for light background and 'white' for dark background
    return 'black' if value >= 180 else 'white'  

def get_text_colordegree_alignment(value):
    # Returns 'black' for light background and 'white' for dark background
    return 'black' if value >= 90 else 'white'  

def get_text_colordistance(value):
    # Returns 'black' for light background and 'white' for dark background
    return 'black' if value > 1.5 else 'white'  


dataFolder = "D:/PhD EXPANSE/Data/Amsterdam"
os.chdir(os.path.join(dataFolder, "Air Pollution Determinants"))

# for matrixsize in [3, 5, 7, 9, 11]:
#     print(f"Matrix size: {matrixsize}")
#     matrix, distances, degrees = create_matrix_and_calculate_vectors(matrixsize)
#     print(f"Matrix:\n{matrix}")
#     print(f"Distances:\n{distances}")
#     print(f"Degrees:\n{degrees}")
#     plt.imshow(distances)
#     plt.colorbar()
#     for i in range(len(distances)):
#         for j in range(len(distances[i])):
#             plt.text(j, i, f'{round(distances[i][j],1)}', ha='center', va='center', color=get_text_colordistance(distances[i][j]))
#     plt.savefig(f"distances{matrixsize}.png",bbox_inches='tight', dpi = 300)
#     plt.close()
#     plt.imshow(degrees)
#     plt.colorbar()
#     for i in range(len(degrees)):
#         for j in range(len(degrees[i])):
#             plt.text(j, i, f'{round(degrees[i][j], 1)}', ha='center', va='center', color=get_text_colordegrees(degrees[i][j]))
#     plt.savefig(f"degrees{matrixsize}.png",bbox_inches='tight', dpi = 300)
#     plt.close()
#     print("\n")


for winddirection in [45, 270, 67]:
    matrix, distances, degrees = create_matrix_and_calculate_vectors(7)
    degree_alignment = abs(degrees - winddirection)
    for i in range(len(degree_alignment)):
        for j in range(len(degree_alignment[i])):
            diff = degree_alignment[i][j]
            diff = min(diff, 360 - diff)
            degree_alignment[i][j] = diff
    
    plt.imshow(degree_alignment)
    plt.colorbar()
    for i in range(len(degree_alignment)):
        for j in range(len(degree_alignment[i])):
            plt.text(j, i, f'{round(degree_alignment[i][j], 1)}', ha='center', va='center', color=get_text_colordegree_alignment(degree_alignment[i][j]))
    center_x, center_y = np.array(matrix.shape) // 2
    wind_dir_rad = np.deg2rad( ((winddirection + 360) % 360)-90)
    arrow_length = 7 / 2  # Adjust the length of the arrow as needed
    arrow_dx = arrow_length * np.cos(wind_dir_rad)
    arrow_dy = arrow_length * np.sin(wind_dir_rad)
    arrow = patches.FancyArrowPatch((center_x, center_y), (center_x + arrow_dx, center_y + arrow_dy),
                                color='red', arrowstyle='<-', linewidth=2.5, mutation_scale=15)
    plt.gca().add_patch(arrow)
    # plt.subplots_adjust(bottom=0.1)
    plt.text(0.5, -0.1, f"Winddirection: {winddirection}° (red arrow)",
                 ha='center', va='center', transform=plt.gca().transAxes)
    plt.savefig(f"degree_alignmentMS{7}_winddirection{winddirection}.png",bbox_inches='tight', dpi = 300)
    plt.close()
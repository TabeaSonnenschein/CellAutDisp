from setuptools import setup, find_packages

# This file contains metadata about your package, such as its name, version, description, dependencies, and other details.
# Example setup.py

setup(
    name='CellAutDisp',
    version='0.1',
    packages=find_packages(),
    install_requires=[
        # List your dependencies here
        'numpy',
        'pandas',
        'matplotlib',
        'seaborn',
        'os',
        'time',
        'joblib',
        'math',
        'geneticalgorithm2',
        'datetime',
        'json',
        'xarray-spatial',
        'geopandas',
        'shapely',
        'scipy',
        'xarray',
        'sklearn'

    ],
    entry_points={
        'console_scripts': [
            'mypackage-cli = mypackage.module1:main_function',
        ],
    },
)
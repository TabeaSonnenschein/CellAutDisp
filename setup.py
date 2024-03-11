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
        'joblib',
        'geneticalgorithm2',
        'datetime',
        'xarray-spatial',
        'geopandas',
        'shapely',
        'scipy',
        'xarray',
        'scikit-learn',
        'pyarrow>=14.0.1'
    ],
    entry_points={
        'console_scripts': [
            'mypackage-cli = mypackage.module1:main_function',
        ],
    },
)
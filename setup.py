from setuptools import setup, find_packages

# This file contains metadata about your package, such as its name, version, description, dependencies, and other details.
# Example setup.py

with open("README.md", "r") as read_file:
    long_description = read_file.read()

setup(
    name='CellAutDisp',
    version='0.1',
    python_requires='>=3.9',
    packages=find_packages(),
    install_requires=[
        # List your dependencies here
        'numpy>=1.23.5',
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
        'pyarrow>=14.0.1',
        'dask_expr',
        'dask==2023.7.1',
        'urllib3==1.26.16',
        'matplotlib_scalebar',
        'func_timeout',
        'rioxarray'
    ],
    entry_points={
        'console_scripts': [
            'CellAutDisp-apply = CellAutDisp.cellautom_dispersion:compute_hourly_dispersion',
        ],
    },
    long_description=long_description,
    long_description_content_type="text/markdown",
)
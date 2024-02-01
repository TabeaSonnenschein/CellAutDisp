from setuptools import setup, find_packages

# This file contains metadata about your package, such as its name, version, description, dependencies, and other details.
# Example setup.py

setup(
    name='mypackage',
    version='0.1',
    packages=find_packages(),
    install_requires=[
        # List your dependencies here
    ],
    entry_points={
        'console_scripts': [
            'mypackage-cli = mypackage.module1:main_function',
        ],
    },
)
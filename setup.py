from setuptools import find_packages, setup

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="hydra",  # Replace with your desired package name
    version="0.1.0",
    author="Your Name",
    author_email="lgallucc@mpi-bremen.de",
    description="Hydrothermal Vent Data Research Analysis Package",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/luigallucci/HYDRA",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
    install_requires=[
        "pandas>=1.0.0",
        "numpy>=1.18.0",
        "matplotlib>=3.0.0",
        "xarray>=0.16.0",
        "scipy>=1.4.0",
        "haversine>=2.4.0",
        "geopy>=2.0.0",
        "argparse>=1.4.0",
        # Add other dependencies as needed
    ],
    include_package_data=True,
    package_data={
        "hydra": ["data/*.csv", "data/*.nc"],  # Adjust based on your data files
    },
    entry_points={
        "console_scripts": [
            "hydra=hydra.cli:main",
        ],
    },
)

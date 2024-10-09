# tests/conftest.py
import os

import pandas as pd
import pytest
import xarray as xr

from hydra import load_all_data
from hydra.config import compute_lat_lon_bounds, config


@pytest.fixture(scope="session")
def data_fixture(tmp_path_factory):
    """
    Fixture to create mock data directories and files for testing.
    """
    # Create a temporary directory for the entire test session
    temp_dir = tmp_path_factory.mktemp("data")

    # Define subdirectories
    bottle_data_dir = temp_dir / "bottle_data"
    profile_data_dir = temp_dir / "profile_data"
    bathymetry_dir = temp_dir / "bathymetry"

    # Create subdirectories
    bottle_data_dir.mkdir(parents=True)
    profile_data_dir.mkdir(parents=True)
    bathymetry_dir.mkdir(parents=True)

    # Create mock CSV files in bottle_data_dir
    bottle_csv_1 = bottle_data_dir / "station1_01_btl.csv"
    bottle_csv_1.write_text(
        "CTD_lon,CTD_lat,LONGITUDE,LATITUDE,TimeS_mean,Bottle\n-74.0060,40.7128,-74.0060,40.7128,100,1\n"
    )

    bottle_csv_2 = bottle_data_dir / "station2_02_btl.csv"
    bottle_csv_2.write_text(
        "CTD_lon,CTD_lat,LONGITUDE,LATITUDE,TimeS_mean,Bottle\n-0.1278,51.5074,-0.1278,51.5074,200,2\n"
    )

    # Create mock CSV files in profile_data_dir (now including 'Bottle' column)
    profile_csv_1 = profile_data_dir / "profile1.csv"
    profile_csv_1.write_text(
        "Dship_lon,Dship_lat,CTD_lon,CTD_lat,LONGITUDE,LATITUDE,timeS,upoly0,CTD_depth,Bottle\n0.1,51.5,-0.1278,51.5074,-0.1278,51.5074,100,0.0,10,1\n0.2,51.6,-0.1278,51.5074,-0.1278,51.5074,200,0.1,20,2"
    )

    # Create mock NetCDF file in bathymetry_dir
    bathymetry_file = bathymetry_dir / "bathymetry.nc"
    ds = xr.Dataset(
        {
            "depth": (("lat", "lon"), [[1000, 2000], [1500, 2500]]),
            "lon": ("lon", [0, 1]),
            "lat": ("lat", [0, 1]),
        }
    )
    ds.to_netcdf(str(bathymetry_file))

    # Mock vents data
    vents = {
        "vent1": {"name": "Vent 1", "coordinates": (0.5, 0.5)},
        "vent2": {"name": "Vent 2", "coordinates": (0.6, 0.6)},
    }

    # Mock DNA and Hydrogen samples dictionary
    bottle_type_dict = {
        "station1": {"DNA": [1], "Hydrogen": [2]},
        "station2": {"DNA": [2]},
    }

    # Compute dynamic latitude and longitude bounds based on mock data
    min_lat, max_lat, min_lon, max_lon = compute_lat_lon_bounds(str(bottle_data_dir))

    # Update the config with the paths to the temporary data and mock data
    config.update(
        {
            "data_paths": {
                "bathymetry_netcdf": str(bathymetry_file),
                "output_dir": str(temp_dir / "output"),
                "bottle_data_dir": str(bottle_data_dir),
                "profile_data_dir": str(profile_data_dir),
            },
            "bathymetry": {
                "lat_bounds": (min_lat, max_lat),
                "lon_bounds": (min_lon, max_lon),
                "elevation_var": config["bathymetry"][
                    "elevation_var"
                ],  # Retain existing value
            },
            "plot_settings": {
                "dpi": config["plot_settings"]["dpi"],
                "num_cols_profiles": config["plot_settings"]["num_cols_profiles"],
                "cmap_orp": config["plot_settings"]["cmap_orp"],
            },
            "vents": vents,
        }
    )

    # Ensure the output directory exists
    (temp_dir / "output").mkdir(parents=True, exist_ok=True)

    # Load all data using the updated config paths, including the bottle_type_dict
    data = load_all_data(
        bottle_data_dir=str(bottle_data_dir),
        profile_data_dir=str(profile_data_dir),
        bathymetry_file=str(bathymetry_file),
        bottle_type_dict=bottle_type_dict,  # Add this argument
        calculate_distances=True,
        method="haversine",
    )

    # Update config with loaded data
    config.update(data)

    return config

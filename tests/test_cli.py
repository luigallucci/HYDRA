# tests/test_cli.py

import json
from unittest.mock import patch

import pandas as pd
import pytest
import xarray as xr

from hydra.cli import main_function


def test_cli_main_function_success(tmp_path):
    """
    Test the CLI's main function with valid arguments.
    """
    # Create mock data directories and files
    bottle_dir = tmp_path / "bottle_data"
    profile_dir = tmp_path / "profile_data"
    bathymetry_file = tmp_path / "bathymetry.nc"
    output_dir = tmp_path / "output"
    bottle_type_file = tmp_path / "bottle_type_dict.json"

    bottle_dir.mkdir()
    profile_dir.mkdir()
    output_dir.mkdir()

    # Create mock bottle data CSV with 'temperature' and 'Bottle' columns
    (bottle_dir / "station1_01_btl.csv").write_text(
        "CTD_lon,CTD_lat,LONGITUDE,LATITUDE,TimeS_mean,Bottle,temperature\n"
        "-74.0060,40.7128,-74.0060,40.7128,12.0,1,15.5\n"
        "-74.0050,40.7138,-74.0050,40.7138,13.0,2,16.0"
    )

    # Create mock profile data CSV with 'temperature' and 'Bottle' columns
    (profile_dir / "profile1.csv").write_text(
        "Dship_lon,Dship_lat,CTD_lon,CTD_lat,LONGITUDE,LATITUDE,timeS,upoly0,CTD_depth,Bottle,temperature\n"
        "-74.0060,40.7128,-74.0060,40.7128,-74.0060,40.7128,12,0.1,100,1,15.5\n"
        "-74.0050,40.7138,-74.0050,40.7138,-74.0050,40.7138,13,0.2,150,2,16.0"
    )

    # Create mock bathymetry NetCDF
    ds = xr.Dataset(
        {"depth": (("lat", "lon"), [[1000, 2000], [1500, 2500]])},
        coords={"lat": [0, 1], "lon": [0, 1]},
    )
    ds.to_netcdf(str(bathymetry_file))

    # Create a bottle type dictionary and save it as a JSON file
    bottle_type_dict = {
        "station1": {"DNA": [1], "Hydrogen": [2]},
        "station2": {"DNA": [2]},
    }
    with open(bottle_type_file, "w") as f:
        json.dump(bottle_type_dict, f)

    # Define CLI arguments, including the path to the bottle_type_dict file
    cli_args = [
        "--bottle_dir",
        str(bottle_dir),
        "--profile_dir",
        str(profile_dir),
        "--bathymetry_file",
        str(bathymetry_file),
        "--output_dir",
        str(output_dir),
        "--bottle_type_dict",
        str(bottle_type_file),  # Pass the file path for the bottle type dictionary
    ]

    # Mock the print function to check the final output message
    with patch("builtins.print") as mock_print:
        main_function(cli_args)
        mock_print.assert_called_with("HYDRA processing complete.")

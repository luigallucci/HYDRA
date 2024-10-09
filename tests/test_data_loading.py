# tests/test_data_loading.py

import os
from pathlib import Path

import pandas as pd
import pytest

from hydra.data_loading import (combine_data, extract_ctd_coordinates,
                                load_all_data, load_csv_files,
                                load_netcdf_files)


def test_load_csv_files_empty(tmp_path):
    """
    Test loading CSV files from an empty directory.
    """
    empty_dir = tmp_path / "empty_dir"
    empty_dir.mkdir()

    data_dict = load_csv_files(
        data_dir=str(empty_dir),
        suffixes_to_remove=["_01_btl", "_02_btl"],
        numeric_columns=[
            "CTD_lon",
            "CTD_lat",
            "LONGITUDE",
            "LATITUDE",
            "TimeS_mean",
            "Bottle",
        ],
        required_columns=[
            "CTD_lon",
            "CTD_lat",
            "LONGITUDE",
            "LATITUDE",
            "TimeS_mean",
            "Bottle",
        ],
    )
    assert (
        data_dict == {}
    ), "Data dictionary should be empty when loading from an empty directory."


def test_load_csv_files_with_files(tmp_path):
    """
    Test loading CSV files from a directory with valid CSV files.
    """
    # Create mock CSV file
    csv_file = tmp_path / "station1_01_btl.csv"
    csv_content = "CTD_lon,CTD_lat,LONGITUDE,LATITUDE,TimeS_mean,Bottle\n-74.0060,40.7128,-74.0060,40.7128,12.0,Value1"
    csv_file.write_text(csv_content)

    data_dict = load_csv_files(
        data_dir=str(tmp_path),
        suffixes_to_remove=["_01_btl", "_02_btl"],
        numeric_columns=[
            "CTD_lon",
            "CTD_lat",
            "LONGITUDE",
            "LATITUDE",
            "TimeS_mean",
            "Bottle",
        ],
        required_columns=[
            "CTD_lon",
            "CTD_lat",
            "LONGITUDE",
            "LATITUDE",
            "TimeS_mean",
            "Bottle",
        ],
    )
    assert (
        "station1" in data_dict
    ), "Cleaned filename should be used as key in data dictionary."
    df = data_dict["station1"]
    assert not df.empty, "Loaded DataFrame should not be empty."
    assert df.loc[0, "CTD_lon"] == -74.0060, "CTD_lon should be correctly loaded."
    assert df.loc[0, "TimeS_mean"] == 12.0, "TimeS_mean should be correctly loaded."


def test_load_csv_files_missing_required_columns(tmp_path):
    """
    Test loading CSV files that are missing required columns.
    """
    # Create mock CSV file missing 'Bottle' column
    csv_file = tmp_path / "station2_02_btl.csv"
    csv_content = "CTD_lon,CTD_lat,LONGITUDE,LATITUDE,TimeS_mean\n-0.1278,51.5074,-0.1278,51.5074,13.0"
    csv_file.write_text(csv_content)

    with pytest.raises(
        KeyError, match="Missing columns .* in file station2_02_btl.csv"
    ):
        load_csv_files(
            data_dir=str(tmp_path),
            suffixes_to_remove=["_01_btl", "_02_btl"],
            numeric_columns=[
                "CTD_lon",
                "CTD_lat",
                "LONGITUDE",
                "LATITUDE",
                "TimeS_mean",
                "Bottle",
            ],
            required_columns=[
                "CTD_lon",
                "CTD_lat",
                "LONGITUDE",
                "LATITUDE",
                "TimeS_mean",
                "Bottle",
            ],
        )


def test_load_csv_files_non_csv_files(tmp_path):
    """
    Test that non-CSV files are ignored when loading data.
    """
    # Create a non-CSV file
    txt_file = tmp_path / "readme.txt"
    txt_file.write_text("This is a text file and should be ignored.")

    # Create a valid CSV file
    csv_file = tmp_path / "station3_01_btl.csv"
    csv_content = "CTD_lon,CTD_lat,LONGITUDE,LATITUDE,TimeS_mean,Bottle\n-0.1278,51.5074,-0.1278,51.5074,14.0,Value3"
    csv_file.write_text(csv_content)

    data_dict = load_csv_files(
        data_dir=str(tmp_path),
        suffixes_to_remove=["_01_btl", "_02_btl"],
        numeric_columns=[
            "CTD_lon",
            "CTD_lat",
            "LONGITUDE",
            "LATITUDE",
            "TimeS_mean",
            "Bottle",
        ],
        required_columns=[
            "CTD_lon",
            "CTD_lat",
            "LONGITUDE",
            "LATITUDE",
            "TimeS_mean",
            "Bottle",
        ],
    )
    assert "station3" in data_dict, "Only CSV files should be loaded."
    assert "readme" not in data_dict, "Non-CSV files should be ignored."


def test_load_netcdf_files_with_valid_data(tmp_path):
    """
    Test loading NetCDF files with valid variables.
    """
    # Create mock NetCDF file
    bathymetry_file = tmp_path / "bathymetry.nc"
    import xarray as xr

    ds = xr.Dataset(
        {"depth": (("lat", "lon"), [[1000, 2000], [1500, 2500]])},
        coords={"lat": [0, 1], "lon": [0, 1]},
    )
    ds.to_netcdf(str(bathymetry_file))

    data_dict = load_netcdf_files(data_dir=str(tmp_path), variable_names=["depth"])
    assert (
        "bathymetry.nc" in data_dict
    ), "NetCDF file should be loaded into data dictionary."
    ds_loaded = data_dict["bathymetry.nc"]
    assert (
        "depth" in ds_loaded.variables
    ), "'depth' variable should be present in the loaded NetCDF dataset."


def test_load_netcdf_files_missing_variables(tmp_path):
    """
    Test loading NetCDF files that are missing required variables.
    """
    # Create mock NetCDF file missing 'depth' variable
    bathymetry_file = tmp_path / "bathymetry_missing.nc"
    import xarray as xr

    ds = xr.Dataset(
        {"elevation": (("lat", "lon"), [[500, 1000], [750, 1250]])},
        coords={"lat": [0, 1], "lon": [0, 1]},
    )
    ds.to_netcdf(str(bathymetry_file))

    with pytest.raises(
        KeyError, match="Missing variables .* in NetCDF file bathymetry_missing.nc"
    ):
        load_netcdf_files(data_dir=str(tmp_path), variable_names=["depth"])


def test_extract_ctd_coordinates():
    """
    Test extracting CTD coordinates from a DataFrame.
    """
    df = pd.DataFrame({"CTD_lat": [40.7128, 51.5074], "CTD_lon": [-74.0060, -0.1278]})
    coords = extract_ctd_coordinates(df, lat_column="CTD_lat", lon_column="CTD_lon")
    expected = [(40.7128, -74.0060), (51.5074, -0.1278)]
    assert (
        coords == expected
    ), "CTD coordinates should be correctly extracted as (lat, lon) tuples."


def test_combine_data_type_error():
    """
    Test that combine_data raises an AttributeError when data_dict is not a dictionary.
    """
    data_dict = [
        pd.DataFrame(
            {
                "CTD_lon": [-74.0060],
                "CTD_lat": [40.7128],
                "LONGITUDE": [-74.0060],
                "LATITUDE": [40.7128],
                "TimeS_mean": [12.0],
                "Bottle": ["Value1"],
            }
        )
    ]

    with pytest.raises(AttributeError, match="'list' object has no attribute 'items'"):
        combine_data(data_dict=data_dict, station_id_column="Station_ID")

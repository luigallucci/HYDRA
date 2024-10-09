# tests/test_plotting.py

import os
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import pytest  # Make sure pytest is imported
import xarray as xr

from hydra.plotting import \
    generalized_map_plot  # Ensure the import paths are correct


def test_generalized_map_plot_with_valid_data(data_fixture, tmp_path):
    """
    Test the generalized_map_plot function with valid data.
    """
    config = data_fixture.copy()
    output_file = tmp_path / "map_plot.png"

    # Mock vents data in config
    config["vents"] = {
        "Vent1": {"coordinates": [40.7128, -74.0060], "name": "Vent1"},
        "Vent2": {"coordinates": [51.5074, -0.1278], "name": "Vent2"},
    }

    # Add bottle_types to config
    config["bottle_types"] = {
        "DNA": {"label": "DNA Samples"},
        "Hydrogen": {"label": "Hydrogen Samples"},
    }

    # Ensure bathymetry has matching dimensions
    bathy = config["bathymetry"]
    bathy = bathy.assign_coords(longitude=bathy["lon"], latitude=bathy["lat"])
    config["bathymetry"] = bathy

    generalized_map_plot(
        config=config,
        include_bathymetry=True,
        include_station_paths=True,
        include_vents=True,
        create_subplots=False,
        subplot_groups=None,
        output_filename=str(output_file),
        plot_all_together=True,
    )

    assert output_file.exists(), "Map plot was not saved."


def test_generalized_map_plot_with_no_data(tmp_path):
    """
    Test the generalized_map_plot function with no data.
    """
    config = {}
    output_file = tmp_path / "map_plot_no_data.png"

    # Add an empty bottle_types to avoid KeyError
    config["bottle_types"] = {}

    generalized_map_plot(
        config=config,
        include_bathymetry=True,
        include_station_paths=True,
        include_vents=True,
        create_subplots=False,
        subplot_groups=None,
        output_filename=str(output_file),
        plot_all_together=True,
    )

    assert output_file.exists(), "Map plot with no data was not saved."


def test_generalized_map_plot_error_handling():
    """
    Test error handling for generalized_map_plot.
    """
    config = {"bathymetry": None, "profile_data": None, "bottle_types": {}}

    try:
        generalized_map_plot(
            config=config,
            include_bathymetry=True,
            include_station_paths=True,
            include_vents=True,
            create_subplots=False,
            subplot_groups=None,
            output_filename="error_plot.png",
            plot_all_together=True,
        )
    except Exception as e:
        pytest.fail(f"Plotting failed with error: {e}")

# tests/test_plotting.py

import os
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import pytest
import xarray as xr

from hydra.plotting import (  # Ensure the import paths are correct
    generalized_map_plot,
    generalized_profile_plot,
)


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

    # Ensure bathymetry has matching dimensions
    bathy = config["bathymetry"]
    bathy = bathy.assign_coords(longitude=bathy["lon"], latitude=bathy["lat"])
    config["bathymetry"] = bathy

    generalized_map_plot(
        config=config,
        include_bathymetry=True,
        include_station_paths=True,
        include_dna_samples=True,
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

    generalized_map_plot(
        config=config,
        include_bathymetry=True,
        include_station_paths=True,
        include_dna_samples=True,
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
    config = {"bathymetry": None, "profile_data": None, "dna_samples": None}

    try:
        generalized_map_plot(
            config=config,
            include_bathymetry=True,
            include_station_paths=True,
            include_dna_samples=True,
            include_vents=True,
            create_subplots=False,
            subplot_groups=None,
            output_filename="error_plot.png",
            plot_all_together=True,
        )
    except Exception as e:
        pytest.fail(f"Plotting failed with error: {e}")


def test_generalized_profile_plot_with_valid_data(data_fixture, tmp_path):
    """
    Test the generalized_profile_plot function with valid data.
    """
    config = data_fixture.copy()
    output_file = tmp_path / "profiles.png"

    # Mock bottle_types in config
    config["bottle_types"] = {
        "Type1": {"label": "Type 1"},
        "Type2": {"label": "Type 2"},
    }

    # Mock cumulative_distances in config
    config["cumulative_distances"] = {
        "Station1": [0, 1.5, 3.0],
        "Station2": [0, 2.0, 4.0],
    }

    generalized_profile_plot(
        config=config,
        stations_to_plot=["Station1", "Station2"],
        axis_config="distance",
        include_bottle_types=["Type1", "Type2"],
        create_subplots=False,
        num_cols=2,
        output_filename=str(output_file),
        plot_all_together=True,
        grouping_list=None,
    )

    assert Path(output_file).exists(), "Profile plot file was not created."


def test_generalized_profile_plot_with_invalid_axis_config(data_fixture, tmp_path):
    """
    Test the generalized_profile_plot function with an invalid axis_config.
    """
    config = data_fixture.copy()
    output_file = tmp_path / "invalid_profiles.png"

    # Ensure 'profile_data' contains 'Station1'
    config["profile_data"] = {
        "Station1": pd.DataFrame(
            {
                "timeS": [0, 1, 2],
                "CTD_depth": [10, 20, 30],
                "Bottle": ["Type1", "Type1", "Type1"],
            }
        )
    }

    # Mock bottle_types in config
    config["bottle_types"] = {"Type1": {"label": "Type 1"}}

    with pytest.raises(ValueError, match="axis_config must be 'time' or 'distance'."):
        generalized_profile_plot(
            config=config,
            stations_to_plot=["Station1"],
            axis_config="invalid_axis",  # Invalid value
            include_bottle_types=["Type1"],
            create_subplots=False,
            num_cols=2,
            output_filename=str(output_file),
            plot_all_together=True,
            grouping_list=None,
        )


def test_generalized_profile_plot_missing_cumulative_distances(data_fixture, tmp_path):
    """
    Test the generalized_profile_plot function when cumulative distances are missing.
    """
    config = data_fixture.copy()
    output_file = tmp_path / "missing_distances_profiles.png"

    # Ensure 'profile_data' contains 'Station1'
    config["profile_data"] = {
        "Station1": pd.DataFrame(
            {
                "timeS": [0, 1, 2],
                "CTD_depth": [10, 20, 30],
                "Bottle": ["Type1", "Type1", "Type1"],
            }
        ),
        "Station2": pd.DataFrame(
            {
                "timeS": [0, 1, 2],
                "CTD_depth": [15, 25, 35],
                "Bottle": ["Type1", "Type1", "Type1"],
            }
        ),
    }

    # Remove 'cumulative_distances' for Station1
    config["cumulative_distances"] = {"Station2": [0, 2.0, 4.0]}

    # Mock bottle_types in config
    config["bottle_types"] = {"Type1": {"label": "Type 1"}}

    with pytest.raises(
        ValueError, match="Cumulative distances not calculated for station Station1."
    ):
        generalized_profile_plot(
            config=config,
            stations_to_plot=["Station1"],
            axis_config="distance",
            include_bottle_types=["Type1"],
            create_subplots=False,
            num_cols=2,
            output_filename=str(output_file),
            plot_all_together=True,
            grouping_list=None,
        )


# If there are any other tests in this file that were present before, they would be listed here and remain unchanged.

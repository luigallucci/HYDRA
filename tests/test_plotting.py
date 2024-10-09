# tests/test_plotting.py

import os
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import pytest
import xarray as xr

from hydra.plotting import (  # Assicurati che il percorso sia corretto
    generalized_map_plot, generalized_profile_plot)


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

    # Assicurati che 'depth', 'lon' e 'lat' abbiano la stessa lunghezza
    bathy = config["bathymetry"]
    bathy = bathy.assign_coords(longitude=bathy["lon"], latitude=bathy["lat"])

    # Stack 'lon' e 'lat' per creare una singola dimensione 'points'
    bathy = bathy.stack(points=("lon", "lat"))

    # Verifica che 'points' abbia la dimensione corretta
    # Nota: Dataset.dims ora restituisce un set di nomi di dimensione, quindi usa 'sizes'
    assert bathy.sizes["points"] == 4, "La dimensione di 'points' dovrebbe essere 4."

    config["bathymetry"] = bathy

    # **Aggiunta dei Dati Mock per 'dna_samples'**
    config["dna_samples"] = [
        {"lon": -74.0060, "lat": 40.7128},
        {"lon": -0.1278, "lat": 51.5074},
    ]

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

    assert Path(output_file).exists(), "Plot file was not created."

    # Optionally, verify the plot content (e.g., number of scatter points)
    # This requires more advanced image analysis which is beyond basic testing


def test_generalized_map_plot_with_no_data(data_fixture, tmp_path):
    """
    Test the generalized_map_plot function with no data.
    """
    config = data_fixture.copy()
    output_file = tmp_path / "no_data_map_plot.png"

    # Configura il test per non includere alcun dato
    config["vents"] = {}
    config["bathymetry"] = None
    config["profile_data"] = {}
    config["dna_samples"] = []

    # Mock bottle_types in config (se necessario)
    config["bottle_types"] = {}

    # Usa pytest.warns per aspettare l'avviso specifico
    with pytest.warns(
        UserWarning, match="No artists with labels found to put in legend."
    ):
        generalized_map_plot(
            config=config,
            include_bathymetry=False,
            include_station_paths=False,
            include_dna_samples=False,
            include_vents=False,
            create_subplots=False,
            subplot_groups=None,
            output_filename=str(output_file),
            plot_all_together=True,
        )

    assert Path(output_file).exists(), "Empty plot file was not created."


def test_generalized_map_plot_error_handling(data_fixture, tmp_path):
    """
    Test the generalized_map_plot function's error handling when required data is missing.
    """
    config = data_fixture.copy()
    output_file = tmp_path / "error_map_plot.png"

    # Remove 'bathymetry' from config to simulate missing data
    config["bathymetry"] = None

    # Mock vents data in config
    config["vents"] = {}

    # Remove 'bottle_data' to simulate missing station data
    config["bottle_data"] = {}

    with pytest.raises(TypeError):
        generalized_map_plot(
            config=config,
            include_bathymetry=True,  # This should raise an error since bathymetry is None
            include_station_paths=True,
            include_dna_samples=True,
            include_vents=True,
            create_subplots=False,
            subplot_groups=None,
            output_filename=str(output_file),
            plot_all_together=True,
        )


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

    # Assicurati che 'profile_data' contenga 'Station1'
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
            axis_config="invalid_axis",  # Valore invalido
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

    # Assicurati che 'profile_data' contenga 'Station1'
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

    # Rimuovi 'cumulative_distances' per Station1
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

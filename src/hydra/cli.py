# src/hydra/cli.py

import argparse
import json
import os

from hydra.data_loading import load_all_data
from hydra.data_processing import combine_data, filter_data_by_temperature
from hydra.plotting import generalized_map_plot, generalized_profile_plot
from hydra.utilities import validate_coordinates


def main_function(args=None):
    """
    Entry point for the HYDRA CLI.
    """
    parser = argparse.ArgumentParser(
        description="HYDRA CLI for processing hydrological data."
    )
    parser.add_argument(
        "--bottle_dir",
        type=str,
        required=True,
        help="Directory containing bottle data CSV files.",
    )
    parser.add_argument(
        "--profile_dir",
        type=str,
        required=True,
        help="Directory containing profile data CSV files.",
    )
    parser.add_argument(
        "--bathymetry_file",
        type=str,
        required=True,
        help="Path to the bathymetry NetCDF file.",
    )
    parser.add_argument(
        "--output_dir", type=str, required=True, help="Output directory for results."
    )
    parser.add_argument(
        "--min_temp",
        type=float,
        default=20.0,
        help="Minimum temperature threshold for filtering.",
    )
    parser.add_argument(
        "--bottle_type_dict",
        type=str,
        required=True,
        help="Path to JSON file containing the mapping of bottle types to stations.",
    )  # Aggiunta dell'argomento per il file JSON con il dizionario
    parser.add_argument("--plot", action="store_true", help="Generate map plots.")
    parser.add_argument(
        "--profile_plot", action="store_true", help="Generate profile plots."
    )

    parsed_args = parser.parse_args(args)

    # Carica il dizionario dei tipi di bottiglie dal file JSON
    try:
        with open(parsed_args.bottle_type_dict, "r") as f:
            bottle_type_dict = json.load(f)
    except Exception as e:
        print(f"Error loading bottle type dictionary: {e}")
        return

    # Load all data
    try:
        data = load_all_data(
            bottle_data_dir=parsed_args.bottle_dir,
            profile_data_dir=parsed_args.profile_dir,
            bathymetry_file=parsed_args.bathymetry_file,
            bottle_type_dict=bottle_type_dict,  # Passa il dizionario dei tipi di bottiglie
            calculate_distances=True,
            method="haversine",
        )
    except Exception as e:
        print(f"Error loading data: {e}")
        return

    # Combine bottle data
    combined_bottle = data.get("combined_bottle_data", None)
    if combined_bottle is None:
        print("Combined bottle data not found.")
        return

    # Validate coordinates
    try:
        validate_coordinates(
            latitudes=combined_bottle["CTD_lat"].tolist(),
            longitudes=combined_bottle["CTD_lon"].tolist(),
        )
    except Exception as e:
        print(f"Coordinate validation error: {e}")
        return

    # Filter data based on temperature
    try:
        filtered_data = filter_data_by_temperature(
            combined_bottle,
            min_temp=parsed_args.min_temp,
            temperature_column="temperature",  # Adjust based on actual column name
        )
    except Exception as e:
        print(f"Data filtering error: {e}")
        return

    # Update config with filtered data
    data["filtered_bottle_data"] = filtered_data

    # Generate plots if requested
    if parsed_args.plot:
        try:
            generalized_map_plot(
                config=data,
                output_filename=os.path.join(parsed_args.output_dir, "map_plot.png"),
            )
            print("Map plot generated successfully.")
        except Exception as e:
            print(f"Error generating map plot: {e}")

    if parsed_args.profile_plot:
        try:
            generalized_profile_plot(
                config=data,
                output_filename=os.path.join(parsed_args.output_dir, "profiles.png"),
            )
            print("Profile plots generated successfully.")
        except Exception as e:
            print(f"Error generating profile plots: {e}")

    print("HYDRA processing complete.")

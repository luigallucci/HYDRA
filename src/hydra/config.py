# src/hydra/config.py

import os

import pandas as pd

# Define static latitude and longitude boundaries as default values
DEFAULT_MIN_LAT = -90.0  # Minimum latitude (Southern Hemisphere limit)
DEFAULT_MAX_LAT = 90.0  # Maximum latitude (Northern Hemisphere limit)
DEFAULT_MIN_LON = -180.0  # Minimum longitude
DEFAULT_MAX_LON = 180.0  # Maximum longitude

# Configuration dictionary with static/default values
config = {
    "bathymetry": {
        "lat_bounds": (DEFAULT_MIN_LAT, DEFAULT_MAX_LAT),
        "lon_bounds": (DEFAULT_MIN_LON, DEFAULT_MAX_LON),
        "elevation_var": "depth",
    },
    "plot_settings": {
        "dpi": 300,
        "num_cols_profiles": 5,
        "cmap_orp": "viridis",
    },
    "vents": {
        "Vent1": {"name": "Vent Alpha", "coordinates": (10, -20)},
        "Vent2": {"name": "Vent Beta", "coordinates": (-15, 30)},
        # Add more vents as needed
    },
    # The 'bottle_types' section is now dynamically handled by the workflow
}


def compute_lat_lon_bounds(bottle_data_dir):
    """
    Compute minimum and maximum latitude and longitude bounds based on bottle data.

    :param bottle_data_dir: Directory containing bottle data CSV files.
    :return: Tuple of (min_lat, max_lat, min_lon, max_lon)
    """
    latitudes = []
    longitudes = []
    for filename in os.listdir(bottle_data_dir):
        if filename.endswith(".csv"):
            file_path = os.path.join(bottle_data_dir, filename)
            df = pd.read_csv(file_path)
            # Ensure required columns exist
            if {"CTD_lat", "CTD_lon"}.issubset(df.columns):
                latitudes.extend(df["CTD_lat"].dropna().tolist())
                longitudes.extend(df["CTD_lon"].dropna().tolist())
            else:
                raise KeyError(
                    f"Required columns 'CTD_lat' and 'CTD_lon' not found in {filename}."
                )

    # Determine bounds with fallback to default if no data
    min_lat = min(latitudes) if latitudes else DEFAULT_MIN_LAT
    max_lat = max(latitudes) if latitudes else DEFAULT_MAX_LAT
    min_lon = min(longitudes) if longitudes else DEFAULT_MIN_LON
    max_lon = max(longitudes) if longitudes else DEFAULT_MAX_LON

    return min_lat, max_lat, min_lon, max_lon


def load_bottle_types(bottle_type_dict):
    """
    Load bottle types into configuration for dynamic assignment of bottle types.

    :param bottle_type_dict: Dictionary mapping station IDs to their corresponding bottle types and numbers.
                             Example: {'Station007': {'DNA': [3, 6, 9], 'Hydrogen': [12, 15, 18]}}
    :return: Updated configuration with bottle types.
    """
    config["bottle_types"] = bottle_type_dict

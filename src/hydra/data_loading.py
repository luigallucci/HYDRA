# src/hydra/data_loading.py

import os

import pandas as pd
import xarray as xr

from hydra.utilities import (  # Assicurati che sia importata
    assign_bottle_types_to_stations, calculate_cumulative_distances)


def load_csv_files(
    data_dir, suffixes_to_remove, numeric_columns, required_columns=None
):
    """
    Load multiple CSV files from a directory, clean their filenames, ensure specified columns are numeric,
    and verify the presence of required columns.
    """
    data = {}
    for filename in os.listdir(data_dir):
        if filename.endswith(".csv"):
            base_name = filename
            # Remove specified suffixes
            for suffix in suffixes_to_remove:
                if filename.endswith(suffix + ".csv"):
                    base_name = filename.replace(suffix, "")
                    break
            base_name = base_name.replace(".csv", "")
            filepath = os.path.join(data_dir, filename)
            df = pd.read_csv(filepath)

            # Check for required columns
            if required_columns:
                missing_cols = [
                    col for col in required_columns if col not in df.columns
                ]
                if missing_cols:
                    raise KeyError(f"Missing columns {missing_cols} in file {filename}")

            # Convert specified columns to numeric, coercing errors
            df[numeric_columns] = df[numeric_columns].apply(
                pd.to_numeric, errors="coerce"
            )
            data[base_name] = df
    return data


def load_netcdf_files_with_zoom(data_dir, variable_names, lat_range=None, lon_range=None):
    """
    Load NetCDF files from the specified directory, focusing on specific variables
    and optionally extracting a zoomed region.

    :param data_dir: Directory containing the NetCDF files.
    :param variable_names: List of variables to extract from each file.
    :param lat_range: Optional tuple (lat_min, lat_max) for zooming into a latitude range.
    :param lon_range: Optional tuple (lon_min, lon_max) for zooming into a longitude range.
    :return: Dictionary of datasets indexed by filenames.
    """
    data = {}
    
    for filename in os.listdir(data_dir):
        if filename.endswith(".nc"):
            file_path = os.path.join(data_dir, filename)
            ds = xr.open_dataset(file_path)
            
            # Ensure the required variables are present
            missing_vars = [var for var in variable_names if var not in ds.variables]
            if missing_vars:
                raise KeyError(f"Missing variables {missing_vars} in NetCDF file {filename}")
            
            # Select the specific region if lat_range and lon_range are provided
            region = ds
            
            if lat_range is not None and lon_range is not None:
                lat_min, lat_max = lat_range
                lon_min, lon_max = lon_range
                
                # Ensure the coordinates are included in the dataset
                if 'lat' in ds and 'lon' in ds:
                    region = ds.sel(lat=slice(lat_min, lat_max), lon=slice(lon_min, lon_max))
                else:
                    raise ValueError("Latitude and Longitude coordinates not found in the dataset.")

            # Keep only the required variables
            data[filename] = region[variable_names]

    return data


def extract_ctd_coordinates(df, lat_column, lon_column):
    """
    Extract CTD coordinates from a DataFrame.
    """
    return list(zip(df[lat_column], df[lon_column]))


def combine_data(data_dict, station_id_column):
    """
    Combine multiple DataFrames into a single DataFrame with a station identifier.
    """
    combined_df = pd.DataFrame()
    for station_id, df in data_dict.items():
        df_copy = df.copy()
        df_copy[station_id_column] = station_id
        combined_df = pd.concat([combined_df, df_copy], ignore_index=True)
    return combined_df

def load_all_data(
    bottle_data_dir,
    profile_data_dir,
    bathymetry_file,
    bottle_type_dict,  # Dizionario per assegnare i tipi di bottiglie
    lat_bounds=None,  # Limiti di latitudine per la batimetria
    lon_bounds=None,  # Limiti di longitudine per la batimetria
    station_filter=None,  # Filtra le stazioni specificate nel config
    suffixes_to_remove_bottle=["_01_btl", "_02_btl"],
    suffixes_to_remove_profile=["_01_cnv", "_02_cnv"],
    bottle_numeric_columns=[
        "CTD_lon",
        "CTD_lat",
        "TimeS_mean",
        "Bottle",
    ],
    profile_numeric_columns=[
        "Dship_lon",
        "Dship_lat",
        "CTD_lon",
        "CTD_lat",
        "timeS",
        "upoly0",
        "CTD_depth",
    ],
    bathymetry_variables=["elevation"],  # Variabili da estrarre dai file NetCDF
    station_id_column="Station_ID",
    extract_coordinates=True,
    calculate_distances=False,
    method="haversine",
):
    """
    Funzione integrata per caricare tutti i dati necessari per HYDRA.
    """
    data = {}

    # Definisci le colonne richieste per i dati delle bottiglie e dei profili
    bottle_required_columns = [
        "CTD_lon",
        "CTD_lat",
        "TimeS_mean",
        "Bottle",
    ]
    profile_required_columns = [
        "Dship_lon",
        "Dship_lat",
        "CTD_lon",
        "CTD_lat",
        "timeS",
        "upoly0",
        "CTD_depth",
    ]

    # Carica i dati delle bottiglie
    data["bottle_data"] = load_csv_files(
        data_dir=bottle_data_dir,
        suffixes_to_remove=suffixes_to_remove_bottle,
        numeric_columns=bottle_numeric_columns,
        required_columns=bottle_required_columns,
    )

    # Filtra le stazioni se specificato
    if station_filter:
        data["bottle_data"] = {
            station_id: df for station_id, df in data["bottle_data"].items()
            if station_id in station_filter
        }

    # Assegna i tipi di bottiglie utilizzando il dizionario
    data["bottle_data"] = assign_bottle_types_to_stations(
        data["bottle_data"], bottle_type_dict
    )

    # Carica i dati dei profili
    data["profile_data"] = load_csv_files(
        data_dir=profile_data_dir,
        suffixes_to_remove=suffixes_to_remove_profile,
        numeric_columns=profile_numeric_columns,
        required_columns=profile_required_columns,
    )

    # Filtra i dati dei profili se specificato
    if station_filter:
        data["profile_data"] = {
            station_id: df for station_id, df in data["profile_data"].items()
            if station_id in station_filter
        }

    # Carica i dati di batimetria
    bathymetry_dir = os.path.dirname(bathymetry_file)
    bathymetry_filename = os.path.basename(bathymetry_file)
    data["bathymetry"] = load_netcdf_files_with_zoom(
        data_dir=bathymetry_dir,
        variable_names=bathymetry_variables,
        lat_range=lat_bounds,  # Passa i limiti di latitudine
        lon_range=lon_bounds   # Passa i limiti di longitudine
    ).get(bathymetry_filename, None)

    if data["bathymetry"] is None:
        raise FileNotFoundError(
            f"Bathymetry file {bathymetry_filename} not found in directory {bathymetry_dir}."
        )

    # Combine bottle data
    data["combined_bottle_data"] = combine_data(
        data_dict=data["bottle_data"], station_id_column=station_id_column
    )

    # Extract CTD coordinates
    if extract_coordinates:
        data["ctd_coordinates"] = {}
        for station_id, df in data["bottle_data"].items():
            coords = extract_ctd_coordinates(
                df, lat_column="CTD_lat", lon_column="CTD_lon"
            )
            data["ctd_coordinates"][station_id] = coords

    # Calculate cumulative distances
    if calculate_distances:
        data["cumulative_distances"] = {}
        for station_id, coords in data["ctd_coordinates"].items():
            distances = calculate_cumulative_distances(coords, method=method)
            data["cumulative_distances"][station_id] = distances

    return data
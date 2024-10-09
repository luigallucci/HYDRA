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


def load_netcdf_files(data_dir, variable_names):
    """
    Load multiple NetCDF files from a directory and extract specified variables.
    """
    data = {}
    for filename in os.listdir(data_dir):
        if filename.endswith(".nc") or filename.endswith(".netcdf"):
            filepath = os.path.join(data_dir, filename)
            ds = xr.open_dataset(filepath)
            # Check if required variables exist
            missing_vars = [var for var in variable_names if var not in ds.variables]
            if missing_vars:
                raise KeyError(
                    f"Missing variables {missing_vars} in NetCDF file {filename}"
                )
            ds = ds[variable_names]
            data[filename] = ds
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
    suffixes_to_remove_bottle=["_01_btl", "_02_btl"],
    suffixes_to_remove_profile=["_01_cnv", "_02_cnv"],
    bottle_numeric_columns=[
        "CTD_lon",
        "CTD_lat",
        "LONGITUDE",
        "LATITUDE",
        "TimeS_mean",
        "Bottle",
    ],
    profile_numeric_columns=[
        "Dship_lon",
        "Dship_lat",
        "CTD_lon",
        "CTD_lat",
        "LONGITUDE",
        "LATITUDE",
        "timeS",
        "upoly0",
        "CTD_depth",
    ],
    bathymetry_variables=["depth"],  # Adjust based on your NetCDF variables
    station_id_column="Station_ID",
    extract_coordinates=True,
    calculate_distances=False,
    method="haversine",
):
    """
    Integrated function to load all necessary data for HYDRA.
    """
    data = {}

    # Define required columns for bottle and profile data
    bottle_required_columns = [
        "CTD_lon",
        "CTD_lat",
        "LONGITUDE",
        "LATITUDE",
        "TimeS_mean",
        "Bottle",
    ]
    profile_required_columns = [
        "Dship_lon",
        "Dship_lat",
        "CTD_lon",
        "CTD_lat",
        "LONGITUDE",
        "LATITUDE",
        "timeS",
        "upoly0",
        "CTD_depth",
    ]

    # Load bottle data
    data["bottle_data"] = load_csv_files(
        data_dir=bottle_data_dir,
        suffixes_to_remove=suffixes_to_remove_bottle,
        numeric_columns=bottle_numeric_columns,
        required_columns=bottle_required_columns,
    )

    # Assegna i tipi di bottiglie utilizzando il dizionario
    data["bottle_data"] = assign_bottle_types_to_stations(
        data["bottle_data"], bottle_type_dict
    )

    # Load profile data
    data["profile_data"] = load_csv_files(
        data_dir=profile_data_dir,
        suffixes_to_remove=suffixes_to_remove_profile,
        numeric_columns=profile_numeric_columns,
        required_columns=profile_required_columns,
    )

    # Load bathymetry data
    bathymetry_dir = os.path.dirname(bathymetry_file)
    bathymetry_filename = os.path.basename(bathymetry_file)
    data["bathymetry"] = load_netcdf_files(
        data_dir=bathymetry_dir, variable_names=bathymetry_variables
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

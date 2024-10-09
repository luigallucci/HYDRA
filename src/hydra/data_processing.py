# src/hydra/data_processing.py

import pandas as pd


def combine_data(data_dict, station_id_column):
    """
    Combine multiple DataFrames into a single DataFrame with a station identifier.

    :param data_dict: Dictionary of DataFrames.
    :param station_id_column: Column name to use as station identifier.
    :return: Combined DataFrame.
    """
    if not isinstance(data_dict, dict):
        raise TypeError("data_dict must be a dictionary")

    combined_df = pd.DataFrame()
    for station_id, df in data_dict.items():
        df = df.copy()
        df[station_id_column] = station_id
        combined_df = pd.concat([combined_df, df], ignore_index=True)
    return combined_df


def filter_data_by_temperature(df, min_temp, temperature_column="temperature"):
    """
    Filter the DataFrame to include only rows where the temperature is greater than or equal to min_temp.

    :param df: pandas DataFrame containing temperature data.
    :param min_temp: Minimum temperature threshold.
    :param temperature_column: Name of the temperature column in the DataFrame.
    :return: Filtered pandas DataFrame.
    """
    if not isinstance(df, pd.DataFrame):
        raise TypeError("df must be a pandas DataFrame.")

    if temperature_column not in df.columns:
        raise KeyError(
            f"Column '{temperature_column}' does not exist in the DataFrame."
        )

    if not isinstance(min_temp, (int, float)):
        raise TypeError("min_temp must be a numeric value.")

    filtered_df = df[df[temperature_column] >= min_temp].reset_index(drop=True)

    return filtered_df

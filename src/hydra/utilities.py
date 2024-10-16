# src/hydra/utilities.py

from geopy.distance import geodesic, great_circle
from haversine import haversine


def validate_coordinates(latitudes, longitudes):
    """
    Validate that latitude and longitude values are within valid ranges and lists are of equal length.

    :param latitudes: List or array of latitudes.
    :param longitudes: List or array of longitudes.
    :return: None. Raises ValueError or TypeError if invalid values are found.
    """
    if len(latitudes) != len(longitudes):
        raise ValueError("Latitude and longitude lists must have the same length.")

    for lat in latitudes:
        if not isinstance(lat, (int, float)):
            raise TypeError(f"Latitude values must be numeric. Invalid value: {lat}")
        if not (-90 <= lat <= 90):
            raise ValueError("Latitude values must be between -90 and 90 degrees.")

    for lon in longitudes:
        if not isinstance(lon, (int, float)):
            raise TypeError(f"Longitude values must be numeric. Invalid value: {lon}")
        if not (-180 <= lon <= 180):
            raise ValueError("Longitude values must be between -180 and 180 degrees.")


def calculate_cumulative_distances(coords, method="geodesic"):
    """
    Calculate cumulative distances between consecutive coordinates.

    :param coords: List of (latitude, longitude) tuples.
    :param method: Distance calculation method ('geodesic', 'great_circle', or 'haversine').
    :return: List of cumulative distances starting with 0.
    """
    if method not in ["geodesic", "great_circle", "haversine"]:
        raise ValueError(
            "Invalid method. Choose 'geodesic', 'great_circle', or 'haversine'."
        )

    cumulative = [0]
    for i in range(1, len(coords)):
        if method == "geodesic":
            distance = geodesic(coords[i - 1], coords[i]).kilometers
        elif method == "great_circle":
            distance = great_circle(coords[i - 1], coords[i]).kilometers
        elif method == "haversine":
            distance = haversine(
                coords[i - 1], coords[i]
            )  # Returns distance in kilometers by default
        cumulative.append(cumulative[-1] + distance)
    return cumulative


def assign_bottle_types_to_stations(bottle_data, bottle_type_dict):
    """
    Assigns bottle types to stations based on the provided bottle type dictionary.

    :param bottle_data: Dictionary of DataFrames containing bottle data for each station.
    :param bottle_type_dict: Dictionary mapping stations to bottle types and bottle numbers.
    :return: Updated bottle data with assigned bottle types.
    """
    for station, df in bottle_data.items():
        # Get the bottle type dictionary for the current station
        types_dict = bottle_type_dict.get(station, {})
        
        if not types_dict:
            print(f"No bottle type information for station {station}, skipping...")
            continue  # Skip this station if no bottle types are available
        
        # Iterate over the bottle types and assign them based on bottle numbers
        for bottle_type, bottle_numbers in types_dict.items():
            if bottle_numbers is not None:
                df.loc[df["Bottle"].isin(bottle_numbers), "Bottle_Type"] = bottle_type
            else:
                print(f"Warning: No bottle numbers found for {bottle_type} in station {station}")

        bottle_data[station] = df
    
    return bottle_data

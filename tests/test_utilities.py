import pytest

from hydra.utilities import (calculate_cumulative_distances,
                             validate_coordinates)


def test_calculate_cumulative_distances_empty():
    """
    Test calculating cumulative distances with an empty list of coordinates.
    """
    coords = []
    distances = calculate_cumulative_distances(coords)
    assert distances == [
        0
    ], "Cumulative distances should start with 0 even when no coordinates are provided."


def test_calculate_cumulative_distances_single_point():
    """
    Test calculating cumulative distances with a single coordinate.
    """
    coords = [(0, 0)]
    distances = calculate_cumulative_distances(coords)
    assert distances == [0], "Cumulative distance for a single point should be [0]."


def test_calculate_cumulative_distances_two_points_haversine():
    """
    Test calculating cumulative distances between two points using the Haversine method.
    """
    coords = [(40.7128, -74.0060), (51.5074, -0.1278)]  # NYC to London
    distances = calculate_cumulative_distances(coords, method="haversine")
    assert (
        len(distances) == 2
    ), "There should be two cumulative distances for two points."
    assert distances[0] == 0, "The first cumulative distance should be 0."
    assert (
        isinstance(distances[1], float) and distances[1] > 0
    ), "The second distance should be a positive float."


def test_calculate_cumulative_distances_two_points_geodesic():
    """
    Test calculating cumulative distances between two points using the Geodesic method.
    """
    coords = [(34.0522, -118.2437), (36.1699, -115.1398)]  # Los Angeles to Las Vegas
    distances = calculate_cumulative_distances(coords, method="geodesic")
    assert (
        len(distances) == 2
    ), "There should be two cumulative distances for two points."
    assert distances[0] == 0, "The first cumulative distance should be 0."
    assert (
        isinstance(distances[1], float) and distances[1] > 0
    ), "The second distance should be a positive float."


def test_calculate_cumulative_distances_multiple_points():
    """
    Test calculating cumulative distances across multiple points.
    """
    coords = [(0, 0), (0, 1), (1, 1)]
    distances = calculate_cumulative_distances(coords, method="haversine")
    assert (
        len(distances) == 3
    ), "There should be three cumulative distances for three points."
    assert distances[0] == 0, "The first cumulative distance should be 0."
    assert distances[1] > 0, "The second cumulative distance should be greater than 0."
    assert (
        distances[2] > distances[1]
    ), "The third cumulative distance should be greater than the second."


def test_validate_coordinates_valid():
    """
    Test validating a set of valid geographic coordinates.
    """
    latitudes = [0, 45, -30]
    longitudes = [0, 120, -150]
    # Should not raise any exception
    try:
        validate_coordinates(latitudes, longitudes)
    except (ValueError, TypeError):
        pytest.fail("validate_coordinates() raised an unexpected exception!")


def test_validate_coordinates_invalid_latitude():
    """
    Test validating coordinates with an invalid latitude.
    """
    latitudes = [0, 95, -30]  # 95 is invalid (valid range: -90 to 90)
    longitudes = [0, 120, -150]
    with pytest.raises(
        ValueError, match="Latitude values must be between -90 and 90 degrees."
    ):
        validate_coordinates(latitudes, longitudes)


def test_validate_coordinates_invalid_longitude():
    """
    Test validating coordinates with an invalid longitude.
    """
    latitudes = [0, 45, -30]
    longitudes = [0, 200, -150]  # 200 is invalid (valid range: -180 to 180)
    with pytest.raises(
        ValueError, match="Longitude values must be between -180 and 180 degrees."
    ):
        validate_coordinates(latitudes, longitudes)


def test_validate_coordinates_mismatched_lengths():
    """
    Test validating coordinates with mismatched lengths of latitude and longitude lists.
    """
    latitudes = [0, 45]
    longitudes = [0, 120, -150]
    with pytest.raises(
        ValueError, match="Latitude and longitude lists must have the same length."
    ):
        validate_coordinates(latitudes, longitudes)


def test_validate_coordinates_invalid_type():
    """
    Test that passing non-numeric types to validate_coordinates raises a TypeError.
    """
    latitudes = [0, "invalid", -30]
    longitudes = [0, 120, -150]
    with pytest.raises(
        TypeError, match="Latitude values must be numeric. Invalid value: invalid"
    ):
        validate_coordinates(latitudes, longitudes)


def test_validate_coordinates_invalid_longitude_type():
    """
    Test that passing non-numeric types to validate_coordinates raises a TypeError for longitude.
    """
    latitudes = [0, 45, -30]
    longitudes = [0, "invalid", -150]
    with pytest.raises(
        TypeError, match="Longitude values must be numeric. Invalid value: invalid"
    ):
        validate_coordinates(latitudes, longitudes)


def test_calculate_cumulative_distances_invalid_method():
    """
    Test calculating cumulative distances with an invalid method.
    """
    coords = [(0, 0), (1, 1)]
    with pytest.raises(
        ValueError,
        match="Invalid method. Choose 'geodesic', 'great_circle', or 'haversine'.",
    ):
        calculate_cumulative_distances(coords, method="invalid_method")

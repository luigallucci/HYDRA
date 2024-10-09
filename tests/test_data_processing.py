# tests/test_data_processing.py

import pandas as pd
import pytest

from hydra.data_processing import combine_data, filter_data_by_temperature


def test_combine_data_empty():
    """
    Test combining data when the input dictionary is empty.
    """
    data_dict = {}
    combined = combine_data(data_dict=data_dict, station_id_column="Station_ID")
    assert (
        combined.empty
    ), "Combined DataFrame should be empty when input data_dict is empty."


def test_combine_data_single_station():
    """
    Test combining data with a single station's data.
    """
    data_dict = {
        "Station1": pd.DataFrame(
            {
                "CTD_lon": [-74.0060],
                "CTD_lat": [40.7128],
                "LONGITUDE": [-74.0060],
                "LATITUDE": [40.7128],
                "TimeS_mean": [12.0],
                "Bottle": ["Value1"],
            }
        )
    }
    combined = combine_data(data_dict=data_dict, station_id_column="Station_ID")

    expected = pd.DataFrame(
        {
            "CTD_lon": [-74.0060],
            "CTD_lat": [40.7128],
            "LONGITUDE": [-74.0060],
            "LATITUDE": [40.7128],
            "TimeS_mean": [12.0],
            "Bottle": ["Value1"],
            "Station_ID": ["Station1"],
        }
    )

    pd.testing.assert_frame_equal(combined.reset_index(drop=True), expected)


def test_combine_data_multiple_stations():
    """
    Test combining data with multiple stations' data.
    """
    data_dict = {
        "Station1": pd.DataFrame(
            {
                "CTD_lon": [-74.0060, -74.0050],
                "CTD_lat": [40.7128, 40.7138],
                "LONGITUDE": [-74.0060, -74.0050],
                "LATITUDE": [40.7128, 40.7138],
                "TimeS_mean": [12.0, 13.0],
                "Bottle": ["Value1", "Value2"],
            }
        ),
        "Station2": pd.DataFrame(
            {
                "CTD_lon": [-0.1278, -0.1288],
                "CTD_lat": [51.5074, 51.5084],
                "LONGITUDE": [-0.1278, -0.1288],
                "LATITUDE": [51.5074, 51.5084],
                "TimeS_mean": [14.0, 15.0],
                "Bottle": ["Value3", "Value4"],
            }
        ),
    }
    combined = combine_data(data_dict=data_dict, station_id_column="Station_ID")

    expected = pd.DataFrame(
        {
            "CTD_lon": [-74.0060, -74.0050, -0.1278, -0.1288],
            "CTD_lat": [40.7128, 40.7138, 51.5074, 51.5084],
            "LONGITUDE": [-74.0060, -74.0050, -0.1278, -0.1288],
            "LATITUDE": [40.7128, 40.7138, 51.5074, 51.5084],
            "TimeS_mean": [12.0, 13.0, 14.0, 15.0],
            "Bottle": ["Value1", "Value2", "Value3", "Value4"],
            "Station_ID": ["Station1", "Station1", "Station2", "Station2"],
        }
    )

    pd.testing.assert_frame_equal(combined.reset_index(drop=True), expected)


def test_filter_data_by_temperature():
    """
    Test filtering data based on temperature thresholds.
    """
    df = pd.DataFrame(
        {
            "CTD_lon": [-74.0060, -74.0050, -0.1278, -0.1288],
            "CTD_lat": [40.7128, 40.7138, 51.5074, 51.5084],
            "LONGITUDE": [-74.0060, -74.0050, -0.1278, -0.1288],
            "LATITUDE": [40.7128, 40.7138, 51.5074, 51.5084],
            "TimeS_mean": [12.0, 13.0, 14.0, 15.0],
            "Bottle": ["Value1", "Value2", "Value3", "Value4"],
            "Station_ID": ["Station1", "Station1", "Station2", "Station2"],
            "temperature": [19.5, 20.5, 21.0, 18.0],
        }
    )

    # Filter for temperatures >= 20
    filtered = filter_data_by_temperature(
        df, min_temp=20, temperature_column="temperature"
    )

    expected = pd.DataFrame(
        {
            "CTD_lon": [-74.0050, -0.1278],
            "CTD_lat": [40.7138, 51.5074],
            "LONGITUDE": [-74.0050, -0.1278],
            "LATITUDE": [40.7138, 51.5074],
            "TimeS_mean": [13.0, 14.0],
            "Bottle": ["Value2", "Value3"],
            "Station_ID": ["Station1", "Station2"],
            "temperature": [20.5, 21.0],
        }
    )

    pd.testing.assert_frame_equal(filtered.reset_index(drop=True), expected)


def test_filter_data_by_temperature_no_matches():
    """
    Test filtering data when no records match the temperature criteria.
    """
    df = pd.DataFrame(
        {
            "CTD_lon": [-74.0060, -74.0050],
            "CTD_lat": [40.7128, 40.7138],
            "LONGITUDE": [-74.0060, -74.0050],
            "LATITUDE": [40.7128, 40.7138],
            "TimeS_mean": [12.0, 13.0],
            "Bottle": ["Value1", "Value2"],
            "Station_ID": ["Station1", "Station1"],
            "temperature": [19.5, 19.8],
        }
    )

    # Filter for temperatures >= 20
    filtered = filter_data_by_temperature(
        df, min_temp=20, temperature_column="temperature"
    )

    assert (
        filtered.empty
    ), "Filtered DataFrame should be empty when no records match the criteria."


def test_filter_data_by_temperature_invalid_column():
    """
    Test filtering data when the specified temperature column does not exist.
    """
    df = pd.DataFrame(
        {
            "CTD_lon": [-74.0060, -74.0050],
            "CTD_lat": [40.7128, 40.7138],
            "LONGITUDE": [-74.0060, -74.0050],
            "LATITUDE": [40.7128, 40.7138],
            "TimeS_mean": [12.0, 13.0],
            "Bottle": ["Value1", "Value2"],
            "Station_ID": ["Station1", "Station1"],
        }
    )

    with pytest.raises(KeyError):
        filter_data_by_temperature(df, min_temp=20, temperature_column="temperature")


def test_extract_dna_samples_from_bottle_data():
    config = {
        "bottle_data": {"SO301_009": "path/to/mock_bottle_data_SO301_009.csv"},
        "dna_samples": {"SO301_009": ["Bottle_1", "Bottle_2"]},
    }

    # Assuming bottle data has the correct mock structure, e.g., using pytest fixtures or mocking
    dna_samples = extract_dna_samples_from_bottle_data(config)

    assert len(dna_samples) == 2
    assert dna_samples[0]["bottle"] == "Bottle_1"
    assert "lon" in dna_samples[0]
    assert "lat" in dna_samples[0]

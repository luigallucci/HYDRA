# src/hydra/__init__.py

from .cli import main_function
from .config import compute_lat_lon_bounds, config
from .data_loading import (
    combine_data,
    extract_ctd_coordinates,
    load_all_data,
    load_csv_files,
    load_netcdf_files,
)
from .data_processing import combine_data, filter_data_by_temperature
from .plotting import generalized_map_plot, generalized_profile_plot
from .utilities import calculate_cumulative_distances, validate_coordinates

__all__ = [
    "config",
    "compute_lat_lon_bounds",
    "load_csv_files",
    "load_netcdf_files",
    "extract_ctd_coordinates",
    "combine_data",
    "load_all_data",
    "filter_data_by_temperature",
    "validate_coordinates",
    "calculate_cumulative_distances",
    "generalized_map_plot",
    "generalized_profile_plot",
    "main_function",
]

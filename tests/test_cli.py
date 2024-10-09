from unittest.mock import patch

import pytest

from hydra.cli import main_function  # Assicurati che il percorso sia corretto


def test_cli_main_function_success(tmp_path):
    """
    Test the CLI's main function with valid arguments.
    """
    # Create mock data directories and files
    bottle_dir = tmp_path / "bottle_data"
    profile_dir = tmp_path / "profile_data"
    bathymetry_file = tmp_path / "bathymetry.nc"
    output_dir = tmp_path / "output"

    bottle_dir.mkdir()
    profile_dir.mkdir()
    output_dir.mkdir()

    # Create mock bottle data CSV with 'temperature' column
    (bottle_dir / "station1_01_btl.csv").write_text(
        "CTD_lon,CTD_lat,LONGITUDE,LATITUDE,TimeS_mean,Bottle,temperature\n"
        "-74.0060,40.7128,-74.0060,40.7128,12.0,Value1,15.5\n"
        "-74.0050,40.7138,-74.0050,40.7138,13.0,Value2,16.0"
    )

    # Create mock profile data CSV with 'temperature' column
    (profile_dir / "profile1.csv").write_text(
        "Dship_lon,Dship_lat,CTD_lon,CTD_lat,LONGITUDE,LATITUDE,timeS,upoly0,CTD_depth,Bottle,temperature\n"
        "-74.0060,40.7128,-74.0060,40.7128,-74.0060,40.7128,12,0.1,100,Type1,15.5\n"
        "-74.0050,40.7138,-74.0050,40.7138,-74.0050,40.7138,13,0.2,150,Type2,16.0"
    )

    # Create mock bathymetry NetCDF
    import xarray as xr

    ds = xr.Dataset(
        {"depth": (("lat", "lon"), [[1000, 2000], [1500, 2500]])},
        coords={"lat": [0, 1], "lon": [0, 1]},
    )
    ds.to_netcdf(str(bathymetry_file))

    # Define CLI arguments
    cli_args = [
        "--bottle_dir",
        str(bottle_dir),
        "--profile_dir",
        str(profile_dir),
        "--bathymetry_file",
        str(bathymetry_file),
        "--output",
        str(output_dir),
    ]

    with patch("builtins.print") as mock_print:
        main_function(cli_args)
        mock_print.assert_called_with("HYDRA processing complete.")

# examples/example_map_plot.py

import os

from hydra import generalized_map_plot, load_all_data
from hydra.config import config


def main():
    # Define paths relative to the project root
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

    bottle_data_dir = os.path.join(
        project_root, "data", "bottle_data"
    )  # Adjust as per your structure
    profile_data_dir = os.path.join(
        project_root, "data", "profile_data"
    )  # Adjust as per your structure
    bathymetry_file = os.path.join(
        project_root, "data", "bathymetry", "bathymetry.nc"
    )  # Adjust as per your structure

    # Load all data with integrated function
    data = load_all_data(
        bottle_data_dir=bottle_data_dir,
        profile_data_dir=profile_data_dir,
        bathymetry_file=bathymetry_file,
        calculate_distances=True,  # Enable distance calculations
        method="haversine",  # Choose 'haversine' or 'geodesic'
    )

    # Update config with loaded data
    config.update(data)

    # Define grouping for plotting (optional)
    subplot_groups = [
        ["Station1", "Station2"],  # Group 1
        ["Station3", "Station4"],  # Group 2
        ["Station5"],  # Group 3
    ]

    # Generate map plots
    generalized_map_plot(
        config=config,
        plot_all_together=False,  # Set to False to create separate plots based on grouping
        create_subplots=True,  # Enable subplots
        subplot_groups=subplot_groups,  # Provide grouping list
        output_filename="hydra_map_grouped.png",
    )

    print("Map plots have been generated and saved as 'hydra_map_grouped.png'.")


if __name__ == "__main__":
    main()

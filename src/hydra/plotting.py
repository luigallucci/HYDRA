import os

import matplotlib.pyplot as plt


def generalized_map_plot(
    config,
    include_bathymetry=True,
    include_station_paths=True,
    include_bottle_types=None,  # Used to specify bottle types
    include_vents=True,
    create_subplots=False,
    subplot_groups=None,
    output_filename="map_plot.png",
    plot_all_together=True,
):
    """
    Generate a generalized map plot with the option to handle multiple bottle types (e.g., DNA, Hydrogen).

    :param config: Configuration dictionary containing data and settings.
    :param include_bathymetry: Include bathymetry data in the plot.
    :param include_station_paths: Include station paths in the plot.
    :param include_bottle_types: List of bottle types to include based on provided dictionaries.
    :param include_vents: Include vents in the plot.
    :param create_subplots: Create subplots for different groups.
    :param subplot_groups: List of lists containing group station IDs.
    :param output_filename: Filename for the output plot.
    :param plot_all_together: If True, plot all data in one plot; else, separate plots.
    :return: None. Saves the plot as a PNG file.
    """
    if include_bottle_types is None:
        include_bottle_types = config.get("bottle_types", {}).keys()

    if plot_all_together:
        plt.figure(figsize=(10, 8))

        # Plot bathymetry data if included
        if include_bathymetry and config.get("bathymetry") is not None:
            bathy = config["bathymetry"]
            lon, lat = bathy["lon"].values.flatten(), bathy["lat"].values.flatten()
            depths = bathy["depth"].values.flatten()

            # Ensure matching sizes for lon, lat, and depths
            if len(lon) == len(lat) == len(depths):
                plt.scatter(
                    lon,
                    lat,
                    c=depths,
                    cmap="viridis",
                    alpha=0.5,
                    label="Bathymetry",
                )
            else:
                # Log the issue instead of raising an error
                print(
                    f"Warning: Mismatch in bathymetry data sizes - Lon: {len(lon)}, Lat: {len(lat)}, Depths: {len(depths)}"
                )

        # Plot station paths if included
        if include_station_paths and config.get("profile_data") is not None:
            for station_id, df in config["profile_data"].items():
                plt.plot(
                    df["CTD_lon"], df["CTD_lat"], label=f"Station {station_id} Path"
                )

        # Plot bottle types using the mapping dictionaries (DNA, Hydrogen, etc.)
        if (
            config.get("bottle_data") is not None
            and config.get("bottle_type_dict") is not None
        ):
            for station_id, df in config["bottle_data"].items():
                for bottle_type, bottles in (
                    config["bottle_type_dict"].get(station_id, {}).items()
                ):
                    if bottle_type in include_bottle_types:
                        subset = df[df["Bottle"].isin(bottles)]
                        plt.scatter(
                            subset["LONGITUDE"],  # Longitude from the bottle data
                            subset["LATITUDE"],  # Latitude from the bottle data
                            label=f"{bottle_type} - {station_id}",
                            marker="x",
                        )

        # Plot hydrothermal vents if included
        if include_vents and config.get("vents") is not None:
            for vent_id, vent_info in config["vents"].items():
                plt.scatter(
                    vent_info["coordinates"][1],  # Longitude
                    vent_info["coordinates"][0],  # Latitude
                    marker="D",
                    color="orange",
                    label=f"Vent {vent_id}",
                )

        # Set plot labels and title
        plt.xlabel("Longitude")
        plt.ylabel("Latitude")
        plt.title("HYDRA Map Plot")
        plt.legend()
        plt.savefig(output_filename)
        plt.close()

    else:
        # Handle multiple plots for each station group if needed
        if create_subplots and subplot_groups:
            num_plots = len(subplot_groups)
            cols = 2
            rows = (num_plots + 1) // cols
            fig, axes = plt.subplots(rows, cols, figsize=(12, 6 * rows))
            axes = axes.flatten()

            for idx, group in enumerate(subplot_groups):
                ax = axes[idx]

                for station_id in group:
                    df = config["bottle_data"].get(station_id, None)
                    if df is not None:
                        ax.scatter(
                            df["LONGITUDE"], df["LATITUDE"], label=station_id, alpha=0.7
                        )

                # Plot bottle types based on the dictionaries
                if config.get("bottle_type_dict") is not None:
                    for bottle_type, bottles in (
                        config["bottle_type_dict"].get(station_id, {}).items()
                    ):
                        if bottle_type in include_bottle_types:
                            subset = df[df["Bottle"].isin(bottles)]
                            ax.scatter(
                                subset["LONGITUDE"],
                                subset["LATITUDE"],
                                label=f"{bottle_type} - {station_id}",
                                marker="s",
                                s=50,
                            )

                # Plot vents in subplots if included
                if include_vents:
                    for vent_id, vent_info in config["vents"].items():
                        ax.scatter(
                            vent_info["coordinates"][1],
                            vent_info["coordinates"][0],
                            marker="^",
                            s=100,
                            label=vent_info["name"],
                        )

                # Add legend only if there are labels
                handles, labels = ax.get_legend_handles_labels()
                if labels:
                    ax.legend()

                ax.set_xlabel("Longitude")
                ax.set_ylabel("Latitude")
                ax.set_title(f"Hydrothermal Vent Map - Group {idx + 1}")

            plt.tight_layout()
            plt.savefig(output_filename, dpi=config["plot_settings"]["dpi"])
            plt.close()


def generalized_profile_plot(
    config,
    stations_to_plot=None,  # List of station IDs
    axis_config="time",  # 'time' or 'distance'
    include_bottle_types=None,  # List of bottle types to include
    create_subplots=False,
    num_cols=2,
    output_filename="profiles.png",
    plot_all_together=True,  # If True, plot all stations in one plot; else, separate plots
    grouping_list=None,  # List of lists containing station IDs for grouping
):
    """
    Generate profile plots for specified stations, allowing visualization of different bottle types (e.g., DNA, Hydrogen).

    :param config: Configuration dictionary containing data and settings.
    :param stations_to_plot: List of station IDs to plot. If None, plot all.
    :param axis_config: 'time' or 'distance' for the x-axis.
    :param include_bottle_types: List of bottle types to include in the plot based on the bottle_type_dict.
    :param create_subplots: Create subplots for different station groups.
    :param num_cols: Number of columns for subplots.
    :param output_filename: Filename for the output plot.
    :param plot_all_together: If True, plot all stations in one plot; if False, plot separately.
    :param grouping_list: List of lists containing station IDs for grouping.
    :return: None. Saves the plot as a PNG file.
    """
    if stations_to_plot is None:
        stations_to_plot = list(config["profile_data"].keys())

    if include_bottle_types is None:
        include_bottle_types = config["bottle_type_dict"].keys()

    if plot_all_together:
        plt.figure(figsize=(12, 8))
        xlabel = ""  # Initialize xlabel
        for station_id in stations_to_plot:
            df = config["profile_data"].get(station_id, None)
            if df is not None:
                if axis_config == "time":
                    x = df["timeS"]
                    xlabel = "Time (s)"
                elif axis_config == "distance":
                    if station_id in config.get("cumulative_distances", {}):
                        x = config["cumulative_distances"][station_id]
                        xlabel = "Distance (km)"
                    else:
                        raise ValueError(
                            f"Cumulative distances not calculated for station {station_id}."
                        )
                else:
                    raise ValueError("axis_config must be 'time' or 'distance'.")

                # Utilizzare il dizionario per i tipi di bottiglie
                bottle_type_dict = config.get("bottle_type_dict", {})
                for bottle_type in include_bottle_types:
                    bottles = bottle_type_dict.get(station_id, {}).get(bottle_type, [])
                    bottle_df = df[
                        df["Bottle"].isin(bottles)
                    ]  # Usa il dizionario per i numeri di bottiglia
                    if not bottle_df.empty:
                        plt.plot(
                            x,
                            bottle_df["CTD_depth"],
                            label=f"{station_id} - {bottle_type}",
                        )

        if xlabel:  # Ensure xlabel is assigned
            plt.xlabel(xlabel)
        plt.ylabel("CTD Depth (m)")
        plt.title("CTD Profiles")

        # Aggiungi legenda solo se ci sono etichette
        handles, labels = plt.gca().get_legend_handles_labels()
        if labels:
            plt.legend()

        plt.savefig(
            output_filename, dpi=config.get("plot_settings", {}).get("dpi", 100)
        )
        plt.close()
    else:
        # Multiple plots, each for a single station or group
        if create_subplots and grouping_list:
            num_groups = len(grouping_list)
            cols = num_cols
            rows = (num_groups + cols - 1) // cols
            fig, axes = plt.subplots(rows, cols, figsize=(6 * cols, 4 * rows))
            axes = axes.flatten()
            for idx, group in enumerate(grouping_list):
                ax = axes[idx]
                xlabel = ""  # Initialize xlabel for each subplot
                for station_id in group:
                    df = config["profile_data"].get(station_id, None)
                    if df is not None:
                        if axis_config == "time":
                            x = df["timeS"]
                            xlabel = "Time (s)"
                        elif axis_config == "distance":
                            if station_id in config.get("cumulative_distances", {}):
                                x = config["cumulative_distances"][station_id]
                                xlabel = "Distance (km)"
                            else:
                                raise ValueError(
                                    f"Cumulative distances not calculated for station {station_id}."
                                )
                        else:
                            raise ValueError(
                                "axis_config must be 'time' or 'distance'."
                            )

                        bottle_type_dict = config.get("bottle_type_dict", {})
                        for bottle_type in include_bottle_types:
                            bottles = bottle_type_dict.get(station_id, {}).get(
                                bottle_type, []
                            )
                            bottle_df = df[df["Bottle"].isin(bottles)]
                            if not bottle_df.empty:
                                ax.plot(
                                    x,
                                    bottle_df["CTD_depth"],
                                    label=f"{station_id} - {bottle_type}",
                                )

                if xlabel:
                    ax.set_xlabel(xlabel)
                ax.set_ylabel("CTD Depth (m)")
                ax.set_title(f"CTD Profiles - Group {idx + 1}")

                # Add legend only if there are labels
                handles, labels = ax.get_legend_handles_labels()
                if labels:
                    ax.legend()
            plt.tight_layout()
            plt.savefig(
                output_filename, dpi=config.get("plot_settings", {}).get("dpi", 100)
            )
            plt.close()
        else:
            # Plot each station separately
            for station_id in stations_to_plot:
                df = config["profile_data"].get(station_id, None)
                if df is not None:
                    plt.figure(figsize=(6, 4))
                    if axis_config == "time":
                        x = df["timeS"]
                        xlabel = "Time (s)"
                    elif axis_config == "distance":
                        if station_id in config.get("cumulative_distances", {}):
                            x = config["cumulative_distances"][station_id]
                            xlabel = "Distance (km)"
                        else:
                            raise ValueError(
                                f"Cumulative distances not calculated for station {station_id}."
                            )
                    else:
                        raise ValueError("axis_config must be 'time' or 'distance'.")

                    bottle_type_dict = config.get("bottle_type_dict", {})
                    for bottle_type in include_bottle_types:
                        bottles = bottle_type_dict.get(station_id, {}).get(
                            bottle_type, []
                        )
                        bottle_df = df[df["Bottle"].isin(bottles)]
                        if not bottle_df.empty:
                            plt.plot(
                                x,
                                bottle_df["CTD_depth"],
                                label=f"{station_id} - {bottle_type}",
                            )

                    if xlabel:
                        plt.xlabel(xlabel)
                    plt.ylabel("CTD Depth (m)")
                    plt.title(f"CTD Profile - {station_id}")

                    # Aggiungi legenda solo se ci sono etichette
                    handles, labels = plt.gca().get_legend_handles_labels()
                    if labels:
                        plt.legend()

                    output_path = (
                        os.path.splitext(output_filename)[0] + f"_{station_id}.png"
                    )
                    plt.savefig(
                        output_path, dpi=config.get("plot_settings", {}).get("dpi", 100)
                    )
                    plt.close()

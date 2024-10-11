import matplotlib.pyplot as plt
import numpy as np
import os

def generalized_map_plot(
    config,
    include_bathymetry=True,
    include_station_paths=True,
    include_bottle_types=None,
    include_vents=True,
    create_subplots=False,
    subplot_groups=None,
    plot_all_together=True,
):
    """
    Generate a generalized map plot with the option to handle multiple bottle types (e.g., DNA, Hydrogen).
    """
    if include_bottle_types is None:
        include_bottle_types = config.get("bottle_type_dict", {}).keys()
        
    # Ensure subplot_groups is not None
    if subplot_groups is None:
        subplot_groups = config.get("subplot_groups", [])

    # Define a color map for the stations, based on the number of unique stations
    num_stations = len(config["stations"]["included"])
    color_map = plt.get_cmap("tab10", num_stations)  # Use qualitative color map with distinct colors
    station_colors = {station: color_map(i) for i, station in enumerate(config["stations"]["included"])}

    # Calculate the overall latitude and longitude bounds for each subgroup
    subgroup_limits = {}

    for group in subplot_groups:
        group_lon = []
        group_lat = []
        # Loop through each station in the group and gather coordinates
        for station_id in group:
            df = config["profile_data"].get(station_id, None)
            if df is not None:
                group_lon.extend(df["CTD_lon"].values)
                group_lat.extend(df["CTD_lat"].values)

        # Debugging: Print collected values for each group
        print(f"Group: {group}")
        print(f"Longitude values: {group_lon}")
        print(f"Latitude values: {group_lat}")

        # Ensure valid coordinates are present before calculating limits
        if group_lon and group_lat:
            subgroup_limits[tuple(group)] = (min(group_lon), max(group_lon), min(group_lat), max(group_lat))  # Store limits for each group
        else:
            print(f"No valid coordinates found for group: {group}")

    if create_subplots and subplot_groups:
        # Create separate plots for each station in the group
        num_groups = len(subplot_groups)
        cols = 2
        rows = (num_groups + cols - 1) // cols  # Dynamic row calculation
        fig, axes = plt.subplots(rows, cols, figsize=(12, 6 * rows))
        axes = axes.flatten()

        for idx, group in enumerate(subplot_groups):
            ax = axes[idx]  # Get the current subplot axis
            plt.sca(ax)  # Set the current axis to ax

            # Plot bathymetry if included
            if include_bathymetry and config.get("bathymetry") is not None:
                bathy = config["bathymetry"]
                lon = bathy["lon"].values
                lat = bathy["lat"].values
                depths = bathy["elevation"].values

                if depths.ndim == 2:
                    depths = depths.reshape(len(lat), len(lon))

                contours = ax.contourf(lon, lat, depths, levels=40, alpha=0.7, cmap="viridis")
                plt.colorbar(contours, label='Depth (m)', ax=ax)

            # Plot station paths and bottle types for each station in the group
            group_lon = []
            group_lat = []
            for station_id in group:
                df = config["profile_data"].get(station_id, None)
                if df is not None:
                    ax.plot(df["CTD_lon"], df["CTD_lat"], color=station_colors[station_id], label=f"Station {station_id}", linestyle='-', linewidth=2)

                    # Collect coordinates for zooming
                    group_lon.extend(df["CTD_lon"].values)
                    group_lat.extend(df["CTD_lat"].values)

                    # Plot bottle types
                    if "Bottle" in df.columns:
                        for bottle_type in include_bottle_types:
                            bottles = config["bottle_type_dict"].get(station_id, {}).get(bottle_type, [])
                            bottle_df = df[df["Bottle"].isin(bottles)]
                            if not bottle_df.empty:
                                ax.scatter(
                                    bottle_df["CTD_lon"],
                                    bottle_df["CTD_lat"],
                                    color=station_colors[station_id],  # Use station color
                                    label=bottle_type,
                                )

            # Set limits for the subplot based on the group's stations with a margin
            if (group_lon and group_lat):
                ax.set_xlim(min(group_lon) - 0.01, max(group_lon) + 0.01)
                ax.set_ylim(min(group_lat) - 0.01, max(group_lat) + 0.01)
            else:
                print(f"No valid coordinates for limits in group: {group}")

            # Plot hydrothermal vents if included
            if include_vents and config.get("vents") is not None:
                for vent_id, vent_info in config["vents"].items():
                    ax.scatter(
                        vent_info["coordinates"][1],
                        vent_info["coordinates"][0],
                        marker="D",
                        color="orange",
                        label=vent_info["name"],
                    )

            # Set plot labels and title
            ax.set_xlabel("Longitude")
            ax.set_ylabel("Latitude")
            ax.set_title(f"{config.get('plot_labels', {}).get('map_title', 'HYDRA Map Plot')} - Group {idx + 1}")
            ax.legend()

        plt.tight_layout()
        plt.savefig(f"{config['output_paths']['subplot']}/map_plot_groups.png", dpi=config["plot_settings"]["dpi"])
        plt.close()

    elif create_subplots and not subplot_groups:
        # Create a single plot for each included station
        for station_id in config["stations"]["included"]:
            plt.figure(figsize=(12, 8))
            
            if include_bathymetry and config.get("bathymetry") is not None:
                bathy = config["bathymetry"]
                lon = bathy["lon"].values
                lat = bathy["lat"].values
                depths = bathy["elevation"].values

                if depths.ndim == 2:
                    depths = depths.reshape(len(lat), len(lon))

                contours = plt.contourf(lon, lat, depths, levels=40, alpha=0.7, cmap="viridis")
                plt.colorbar(contours, label='Depth (m)')
                plt.xlim(lon.min(), lon.max())
                plt.ylim(lat.min(), lat.max())

            # Plot the station path
            df = config["profile_data"].get(station_id, None)
            if df is not None:
                plt.plot(df["CTD_lon"], df["CTD_lat"], color=station_colors[station_id], label=f"Station {station_id}", linestyle='-', linewidth=2)

                # Plot bottle types
                if "Bottle" in df.columns:
                    for bottle_type in include_bottle_types:
                        bottles = config["bottle_type_dict"].get(station_id, {}).get(bottle_type, [])
                        bottle_df = df[df["Bottle"].isin(bottles)]
                        if not bottle_df.empty:
                            plt.scatter(
                                bottle_df["CTD_lon"],
                                bottle_df["CTD_lat"],
                                color=station_colors[station_id],  # Use station color
                                label=bottle_type,
                            )

            # Set limits for the individual plot based on the station's data with a margin
            if df is not None:
                plt.xlim(df["CTD_lon"].min() - 0.01, df["CTD_lon"].max() + 0.01)
                plt.ylim(df["CTD_lat"].min() - 0.01, df["CTD_lat"].max() + 0.01)

            # Plot hydrothermal vents if included
            if include_vents:
                for vent_id, vent_info in config["vents"].items():
                    plt.scatter(
                        vent_info["coordinates"][1],
                        vent_info["coordinates"][0],
                        marker="^",
                        s=100,
                        color="orange",
                        label=vent_info["name"],
                    )

            plt.xlabel("Longitude")
            plt.ylabel("Latitude")
            plt.title(config.get("plot_labels", {}).get("map_title", "HYDRA Map Plot"))
            plt.legend()
            plt.tight_layout()

            # Save each station's plot separately
            plt.savefig(f"{config['output_paths']['subplot']}/map_plot_{station_id}.png", dpi=config["plot_settings"]["dpi"])
            plt.close()

    else:
        # Classic behavior for plotting all together
        plt.figure(figsize=(12, 8))

        # Plot bathymetry data if included
        if include_bathymetry and config.get("bathymetry") is not None:
            bathy = config["bathymetry"]
            lon = bathy["lon"].values
            lat = bathy["lat"].values
            depths = bathy["elevation"].values

            if depths.ndim == 2:
                depths = depths.reshape(len(lat), len(lon))

            contours = plt.contourf(lon, lat, depths, levels=40, alpha=0.7, cmap="viridis")
            plt.colorbar(contours, label='Depth (m)')
            plt.xlim(lon.min(), lon.max())
            plt.ylim(lat.min(), lat.max())

        # Plot station paths and bottle types for all stations included
        all_lon = []
        all_lat = []
        for station_id in config["stations"]["included"]:
            df = config["profile_data"].get(station_id, None)
            if df is not None:
                plt.plot(df["CTD_lon"], df["CTD_lat"], color=station_colors[station_id], label=f"Station {station_id}", linestyle='-', linewidth=2)

                # Collect coordinates for zooming
                all_lon.extend(df["CTD_lon"].values)
                all_lat.extend(df["CTD_lat"].values)

                # Plot bottle types
                if "Bottle" in df.columns:
                    for bottle_type in include_bottle_types:
                        bottles = config["bottle_type_dict"].get(station_id, {}).get(bottle_type, [])
                        bottle_df = df[df["Bottle"].isin(bottles)]
                        if not bottle_df.empty:
                            plt.scatter(
                                bottle_df["CTD_lon"],
                                bottle_df["CTD_lat"],
                                color=station_colors[station_id],  # Use station color
                                label=bottle_type,
                            )

        # Set limits with a margin for all stations
        if all_lon and all_lat:
            plt.xlim(min(all_lon) - 0.01, max(all_lon) + 0.01)
            plt.ylim(min(all_lat) - 0.01, max(all_lat) + 0.01)

        # Plot hydrothermal vents if included
        if include_vents:
            for vent_id, vent_info in config["vents"].items():
                plt.scatter(
                    vent_info["coordinates"][1],
                    vent_info["coordinates"][0],
                    marker="^",
                    s=100,
                    color="orange",
                    label=vent_info["name"],
                )

        # Set plot labels and title
        plt.xlabel("Longitude")
        plt.ylabel("Latitude")
        plt.title(config.get("plot_labels", {}).get("map_title", "HYDRA Map Plot"))
        plt.legend()
        plt.tight_layout()  # Adjust layout for better spacing
        plt.savefig(config["output_paths"]["map"], dpi=config["plot_settings"]["dpi"])
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

    # If creating subplots and grouping is defined
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
                        raise ValueError("axis_config must be 'time' or 'distance'.")

                    bottle_type_dict = config.get("bottle_type_dict", {})
                    for bottle_type in include_bottle_types:
                        bottles = bottle_type_dict.get(station_id, {}).get(bottle_type, [])
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
            ax.set_title(f"{config.get('plot_labels', {}).get('profile_title', 'CTD Profiles')} - Group {idx + 1}")

            # Add legend only if there are labels
            handles, labels = ax.get_legend_handles_labels()
            if labels:
                ax.legend()

        plt.tight_layout()

        # Save each group plot separately with an adaptable name
        plt.savefig(
            f"{config['output_paths']['subplot']}/profile_plot_group.png",
            dpi=config.get("plot_settings", {}).get("dpi", 100)
        )
        plt.close()

    elif plot_all_together:
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

                # Use the dictionary for bottle types
                bottle_type_dict = config.get("bottle_type_dict", {})
                for bottle_type in include_bottle_types:
                    bottles = bottle_type_dict.get(station_id, {}).get(bottle_type, [])
                    bottle_df = df[df["Bottle"].isin(bottles)]  # Use the dictionary for bottle numbers
                    if not bottle_df.empty:
                        plt.plot(
                            x,
                            bottle_df["CTD_depth"],
                            label=f"{station_id} - {bottle_type}",
                        )

        if xlabel:  # Ensure xlabel is assigned
            plt.xlabel(xlabel)
        plt.ylabel("CTD Depth (m)")
        plt.title(config.get("plot_labels", {}).get("profile_title", "CTD Profiles"))

        # Add legend only if there are labels
        handles, labels = plt.gca().get_legend_handles_labels()
        if labels:
            plt.legend()

        plt.savefig(
            config["output_paths"]["profile"],  # Use the path from config
            dpi=config.get("plot_settings", {}).get("dpi", 100)
        )
        plt.close()
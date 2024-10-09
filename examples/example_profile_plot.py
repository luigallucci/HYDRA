# examples/example_profile_plot.py

from hydra import generalized_profile_plot
from hydra.config import \
    config  # Assuming config is defined in hydra/config.py

# Define grouping list
grouping_list = [["Station1", "Station2"], ["Station3", "Station4"], ["Station5"]]

# Generate grouped profile plots
generalized_profile_plot(
    config=config,
    plot_all_together=False,
    create_subplots=True,
    grouping_list=grouping_list,
    axis_config="time",
    output_filename="hydra_profiles_grouped.png",
)

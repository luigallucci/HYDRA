# HYDRA

**HYDRA** (Hydrothermal Vent Data Research Analysis) is a Python package designed for comprehensive analysis and visualization of hydrothermal vent data. It offers flexible and customizable plotting and mapping functionalities to aid researchers in their studies.

## Features

- **Data Loading & Cleaning**: Easily import and preprocess CSV and NetCDF datasets.
- **Hydrothermal Vent Mapping**: Visualize vent locations with bathymetric overlays.
- **Station Path Plotting**: Track CTD profiles and station movements.
- **Bottle Data Representation**: Categorize and plot various bottle types with customizable labels and colors.
- **ORP Analysis**: Generate heatmaps for Oxidation-Reduction Potential (ORP) data.
- **Fully Personalized Configurations**: Customize vent names, coordinates, bottle types, and plotting preferences via a centralized configuration.

## Installation

### Using `pip`

```bash
pip install hydra
```

### From source

```bash
git clone https://github.com/yourusername/HYDRA.git
cd HYDRA
pip install -e .
```

## Usage

```python
from hydra import generalized_map_plot, generalized_profile_plot

# Define your configuration
config = {
    # ... (as defined in the configuration structure)
}

# Plotting maps
generalized_map_plot(
    config=config,
    include_bathymetry=True,
    include_station_paths=True,
    include_dna_samples=True,
    include_vents=True,
    create_subplots=True,
    subplot_groups=[['Station1', 'Station2'], ['Station3', 'Station4']],
    output_filename='map.png'
)

# Plotting profiles
generalized_profile_plot(
    config=config,
    stations_to_plot=['Station1', 'Station2'],
    axis_config='time',
    include_bottle_types=['DNA', 'Common'],
    create_subplots=True,
    num_cols=2,
    output_filename='profiles.png'
)
```

## Configuration

Customize your analysis by modifying the config dictionary. Define vents, stations, bottle types, data paths, and plotting settings.

```python

config = {
    'vents': {
        # Define vents
    },
    'stations': {
        # Define stations and their bottle types
    },
    'bottle_types': {
        # Define bottle types with labels and colors
    },
    'data_paths': {
        # Specify data directories and files
    },
    'bathymetry': {
        # Define bathymetry parameters
    },
    'plot_settings': {
        # Customize plotting settings
    }
}
```

## Documentation

Detailed documentation is available in the docs directory, generated using Sphinx.

## Contributing

Contributions are welcome! Please open issues and submit pull requests for enhancements and bug fixes.
## License

This project is licensed under the MIT License.


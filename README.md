# Hydra

![Hydra Logo](image/HYDRA_logo.png) <!-- Replace with your actual logo URL -->

## 📖 Description

**Hydra** is an advanced tool designed for loading, processing, and visualizing oceanographic data. It facilitates the analysis of data from various monitoring stations by supporting the import of CSV and NetCDF files, processing CTD (Conductivity, Temperature, Depth) data, managing DNA samples, and visualizing hydrothermal vents and bathymetry through customizable maps and profiles.

## 🚀 Features

- **Data Loading:** Easily import data from CSV and NetCDF files.
- **Data Processing:** Combine and filter data based on specific criteria such as temperature.
- **Cumulative Distance Calculation:** Calculate cumulative distances between geographic coordinates using methods like Haversine and Geodesic.
- **Visualization:** Generate detailed maps with bathymetry, station paths, DNA samples, and hydrothermal vents.
- **Command-Line Interface (CLI):** Facilitate the execution of common operations directly from the terminal.
- **Comprehensive Testing:** Extensive test coverage to ensure code reliability.
- **Continuous Integration:** Configured with GitHub Actions to automate testing and deployment.


## Table of Contents

- [Installation](#Installation)
- [Usage](#Usage)
- [Contributing](#Contributing)

## 📥 Installation

### Prerequisites

- **Python 3.10** or higher
- **pip** package manager

### Steps

1. **Clone the Repository**

   ```bash
   git clone https://github.com/lgallucc/HYDRA.git
   cd hydra
   ```
2.	**Create a Virtual Environment (Optional but Recommended)**
```bash
python3 -m venv env
source env/bin/activate  # On Windows: env\Scripts\activate
```

3. **Install dependencies**

```bash
pip install -r requirements.txt
```

4. **Install Hydra**

```bash
pip install .
```

## 🛠 Usage

### Command-Line Interface (CLI)

Hydra provides a CLI to facilitate the exuction of common operations. Below are some example of how to use it.

#### Data loading

```bash 
hydra process-data --filter-temperature --temperature-threshold 10
```

#### Data processing

```bash 
hydra load-data --csv-paths path/to/csv1.csv path/to/csv2.csv --netcdf-paths path/to/data1.nc path/to/data2.nc
```

#### Cumulative distance calculation

```bash 
hydra calculate-distances --method haversine --output distances.json
```

#### Generating maps

```bash 
hydra plot map --output map_plot.png --include-bathymetry --include-vents --include-dna-samples
```

#### Generating profiles

```bash 
hydra plot profile --stations Station1 Station2 --output profile_plot.png --axis-config distance
```

### Using the Python API

Hydra can also be used as a Python library to integrate its functionalities into your scripts.

#### Example: Loading and Processing Data

```bash
from hydra.data_loading import load_csv_files, load_netcdf_files, combine_data
from hydra.data_processing import filter_data_by_temperature

# Load data
csv_data = load_csv_files(['path/to/csv1.csv', 'path/to/csv2.csv'])
netcdf_data = load_netcdf_files(['path/to/data1.nc', 'path/to/data2.nc'])

# Combine data
combined_data = combine_data(data_dict={'csv': csv_data, 'netcdf': netcdf_data}, station_id_column='Station_ID')

# Filter data by temperature
filtered_data = filter_data_by_temperature(combined_data, column='temperature', threshold=10)
```

#### Example: Generating a Map

```bash
from hydra.plotting import generalized_map_plot

# Configure parameters
config = {
    'bathymetry': bathy_dataset,
    'vents': vents_data,
    'profile_data': profile_data,
    'dna_samples': dna_samples_data
}

# Generate the map
generalized_map_plot(
    config=config,
    include_bathymetry=True,
    include_station_paths=True,
    include_dna_samples=True,
    include_vents=True,
    create_subplots=False,
    subplot_groups=None,
    output_filename='map_plot.png',
    plot_all_together=True
)
```

## 🤝 Contributing

Contributions are welcome! To contribute, follow these steps:

1.	**Fork the Repository**
2.	**Create a Branch for Your Feature**

```bash
git checkout -b feature/your-feature
```

3.	**Make Your Changes and Commit**

```bash
git commit -m "Add new feature"
```

4. **Push the branch**

```bash
git push origin feature/your-feature
```

5. **Create a pull request**

Explain clearly the changes made and why they should be merged.

## 📝 License

Distributed under the MIT License. See the LICENSE file for more information.

## 📫 Contact

For any questions or requests, you can contact me at lgallucc@mpi-bremen.de

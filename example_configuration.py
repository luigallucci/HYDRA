# Kairei Hydrothermal Field Analysis Configuration
analysis_name: "Kairei Hydrothermal Field Data Analysis"
output_directory: "/path/to/output"  # Modify this with your desired output path

bathymetry:
  file_path: "/path/to/bathymetry_data.nc"  # Adjust to the path of your bathymetry data file
  variable_names:
    lon: "longitude"
    lat: "latitude"
    depth: "depth"

profile_data:
  # Provide paths to your CTD profiles per station
  SO301_009: "/path/to/ctd_data/SO301_009_profile.csv"
  SO301_010: "/path/to/ctd_data/SO301_010_profile.csv"
  # Add other stations as needed

bottle_data:
  # Provide paths to your bottle data per station
  SO301_009: "/path/to/bottle_data/SO301_009_bottle.csv"
  SO301_010: "/path/to/bottle_data/SO301_010_bottle.csv"
  # Continue for other stations

dna_samples:
  # Provide information about DNA samples
  - station_id: "SO301_009"
    sample_id: "DNA_001"
    lon: -69.725
    lat: 33.445
  - station_id: "SO301_010"
    sample_id: "DNA_002"
    lon: -69.731
    lat: 33.451
  # Add other samples as needed

vents:
  # Vent locations in the Kairei field
  Vent1:
    name: "Kairei Vent 1"
    coordinates: [-69.725, 33.445]  # Lon, Lat
  Vent2:
    name: "Kairei Vent 2"
    coordinates: [-69.731, 33.451]

plot_settings:
  dpi: 300
  color_map: "viridis"  # Can be adjusted based on preference

# Settings for specific plots
plot_configurations:
  include_bathymetry: True
  include_station_paths: True
  include_dna_samples: True
  include_vents: True
  create_subplots: True
  subplot_groups:
    - ["SO301_009", "SO301_010"]  # Customize groups of stations for subplots
    - ["SO301_011", "SO301_012"]
  output_filename: "kairei_analysis_map.png"
  plot_all_together: False
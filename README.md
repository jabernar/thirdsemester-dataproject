# Data Visualization Project — GDP Per Capita South America

My project generates three interactive visualizations of GDP per capita trends across South American countries from 2014 to 2024.

## Overview

Visualization of World Bank data on GDP per capita for the 12 South American countries, using three complementary charts:

1. **Line Chart** (`grafico1_linha.png`): Historical trend analysis for 6 countries with complete time-series data (2014–2024)
2. **Bar Chart** (`grafico2_barras.png`): Comparative view of 2024 GDP per capita values across all tracked countries
3. **Choropleth Map** (`grafico3_coropleto.png`): Geographic visualization of South America with countries colored by their 2024 GDP per capita

## Data Source

- **GDP Data**: World Bank — [World Bank GDP Indicator](https://data.worldbank.org/indicator/NY.GDP.PCAP.CD)
- **Geographic Data**: [geo-countries GeoJSON](https://github.com/datasets/geo-countries/)

## Setup

### Requirements

- Python 3.8+
- Dependencies in `requirements.txt`

### Install

1. repository:
   ```bash
   git clone https://github.com/jabernar/thirdsemester-dataproject.git
   cd thirdsemester-dataproject
   ```

2. dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

Run the script to generate visualizations

```bash
python projetodevisualizacaojaime.py
```

Output files will be saved to the `output/` directory:
- `grafico1_linha.png` — Line chart with historical trends
- `grafico2_barras.png` — Bar chart of 2024 GDP per capita
- `grafico3_coropleto.png` — Choropleth map

## Project Structure

```
.
├── README.md                      # This file
├── requirements.txt               # Python dependencies
├── dados_pib.csv                  # GDP data (source: World Bank)
├── projetodevisualizacaojaime.py  # Main visualization script
└── output/                        # Generated charts (created on first run)
    ├── grafico1_linha.png
    ├── grafico2_barras.png
    └── grafico3_coropleto.png
```

## Code Quality Improvements

This refactored version includes:

- **Modular Design**: Functions for each chart type and data loading
- **Configuration Management**: Centralized constants for easy customization
- **Error Handling**: Robust exception handling for network and file I/O operations
- **Logging**: Detailed logging of execution steps for debugging
- **Data Management**: Separated data into a CSV file for maintainability
- **SSL Security**: Proper SSL certificate validation (removed `verify=False`)
- **Retry Logic**: Automatic retry mechanism for network requests
- **Documentation**: Comprehensive docstrings and README

## Key Features

### Chart 1: Line Chart (Historical Trends)
- Shows GDP per capita evolution for 6 countries with complete historical data
- Helps identify economic trends and fluctuations over time
- Countries: Brasil, Chile, Argentina, Colômbia, Peru, Uruguai

### Chart 2: Bar Chart (2024 Comparison)
- Ranks all 12 South American countries by GDP per capita in 2024
- Includes value labels for easy reference
- Better representation of per-capita metrics than pie chart (which only shows relative proportions)

### Chart 3: Choropleth Map (Geographic Distribution)
- Visualizes all countries with a geographic perspective
- Color-coded by GDP per capita value
- Includes annotations with country names

## Customization

Edit the configuration section at the top of `projetodevisualizacaojaime.py` to customize:

- `DATA_FILE`: Path to GDP data CSV
- `OUTPUT_DIR`: Output directory for generated charts
- `CHART_DPI`: Resolution of output images
- `COUNTRY_METADATA`: Country names, colors, and ISO3 codes

## Updating Data

To update GDP data:

1. Download the latest data from [World Bank GDP Indicator](https://data.worldbank.org/indicator/NY.GDP.PCAP.CD)
2. Update `dados_pib.csv` with new values
3. Run the script to regenerate visualizations

## Notes

- The GeoJSON file is downloaded automatically on first run and cached locally
- All output files are high-resolution (150 DPI) suitable for presentations
- Currency values are displayed in USD (current dollars)
- Portuguese naming conventions are maintained for regional context

## Author

Jaime Bernar — Data Visualization Project (3rd Semester)

## License

This project is provided as-is for educational purposes.

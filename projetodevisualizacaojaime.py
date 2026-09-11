"""Data Visualization — GDP Per Capita South America

This module has three visualizations of GDP per capita trends in South American countries from 2014 to 2024.

Data Source: World Bank — https://data.worldbank.org/indicator/NY.GDP.PCAP.CD
GeoJSON Source: https://github.com/datasets/geo-countries
"""

import os
import sys
import logging
from dataclasses import dataclass
from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import matplotlib.patches as mpatches
import seaborn as sns
import geopandas as gpd
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

DATA_FILE = "dados_pib.csv"
OUTPUT_DIR = "output"
GEOJSON_PATH = Path(OUTPUT_DIR) / "countries.geojson"

CHART_DPI = 150
CHART_FONT_SIZE = 11
DEFAULT_COLOR = "#808080"

GEOJSON_URL = (
    "https://raw.githubusercontent.com/datasets/geo-countries/master/data/countries.geojson"
)


@dataclass(frozen=True)
class CountryInfo:
    name: str
    color: str


COUNTRY_METADATA = {
    "URY": CountryInfo("Uruguay", "#8c564b"),
    "CHL": CountryInfo("Chile", "#ff7f0e"),
    "ARG": CountryInfo("Argentina", "#2ca02c"),
    "BRA": CountryInfo("Brazil", "#1f77b4"),
    "GUY": CountryInfo("Guyana", "#aec7e8"),
    "PER": CountryInfo("Peru", "#9467bd"),
    "COL": CountryInfo("Colombia", "#d62728"),
    "SUR": CountryInfo("Suriname", "#c5b0d5"),
    "ECU": CountryInfo("Ecuador", "#ffbb78"),
    "PRY": CountryInfo("Paraguay", "#98df8a"),
    "VEN": CountryInfo("Venezuela", "#ff9896"),
    "BOL": CountryInfo("Bolivia", "#c49c94"),
}

COUNTRY_COLOR_BY_NAME = {info.name: info.color for info in COUNTRY_METADATA.values()}

COUNTRIES_WITH_TIMESERIES = ["BRA", "CHL", "ARG", "COL", "PER", "URY"]


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s — %(levelname)s — %(message)s",
)
logger = logging.getLogger(__name__)


def create_session_with_retries(max_retries=3, backoff_factor=0.5):
    session = requests.Session()
    retry_strategy = Retry(
        total=max_retries,
        backoff_factor=backoff_factor,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["GET"],
    )
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    return session


def download_geojson(url, output_path):
    try:
        logger.info(f"Downloading GeoJSON from {url}...")
        session = create_session_with_retries()
        response = session.get(url, timeout=10)
        response.raise_for_status()

        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w") as f:
            f.write(response.text)
        logger.info(f"GeoJSON saved to {output_path}")
    except requests.RequestException as e:
        logger.error(f"Failed to download GeoJSON: {e}")
        raise


def load_data(csv_file):
    if not os.path.exists(csv_file):
        raise FileNotFoundError(f"Data file not found: {csv_file}")
    logger.info(f"Loading data from {csv_file}...")
    df = pd.read_csv(csv_file)
    logger.info(f"Loaded data for {len(df)} countries")
    return df


def get_year_columns(df):
    return sorted((col for col in df.columns if col.isdigit()), key=int)


def validate_countries(df):
    known_names = set(COUNTRY_COLOR_BY_NAME.keys())
    unknown = set(df["Pais"]) - known_names
    if unknown:
        logger.warning(
            f"Countries not found in COUNTRY_METADATA (will use default color): "
            f"{sorted(unknown)}"
        )


def prepare_timeseries_data(df):
    years = get_year_columns(df)
    timeseries = {}
    for _, row in df.iterrows():
        pais = row["Pais"]
        valores = [row[year] for year in years]
        timeseries[pais] = valores
    return timeseries, [int(year) for year in years]


def prepare_2024_data(df):
    last_year_col = get_year_columns(df)[-1]
    return df.set_index("Pais")[last_year_col].to_dict()


def get_country_color(country_name):
    return COUNTRY_COLOR_BY_NAME.get(country_name, DEFAULT_COLOR)


def generate_line_chart(timeseries_data, years, output_file):
    logger.info("Generating line chart...")
    fig, ax = plt.subplots(figsize=(12, 6))

    for pais, valores in timeseries_data.items():
        color = get_country_color(pais)
        ax.plot(
            years,
            valores,
            marker="o",
            markersize=5,
            linewidth=2.5,
            label=pais,
            color=color,
        )

    ax.set_title(
        "PIB per capita — América do Sul (2014–2024)",
        fontsize=14,
        fontweight="bold",
        pad=15,
    )
    ax.set_xlabel("Ano", fontsize=11)
    ax.set_ylabel("PIB per capita (US$ correntes)", fontsize=11)
    ax.yaxis.set_major_formatter(
        mticker.FuncFormatter(lambda x, _: f"US$ {x:,.0f}")
    )
    ax.set_xticks(years)
    ax.tick_params(axis="x", labelrotation=45)
    ax.legend(bbox_to_anchor=(1.02, 1), loc="upper left", fontsize=10)
    ax.grid(axis="y", linestyle="--", alpha=0.4)
    sns.despine(ax=ax)
    plt.tight_layout()
    plt.savefig(output_file, dpi=CHART_DPI, bbox_inches="tight")
    plt.close()
    logger.info(f"Line chart saved to {output_file}")


def generate_bar_chart(data_2024, output_file):
    logger.info("Generating bar chart...")
    # Sort countries by GDP value for better visualization
    sorted_data = dict(sorted(data_2024.items(), key=lambda x: x[1], reverse=True))

    fig, ax = plt.subplots(figsize=(10, 6))

    countries = list(sorted_data.keys())
    values = list(sorted_data.values())
    colors = [get_country_color(c) for c in countries]

    bars = ax.bar(countries, values, color=colors, edgecolor="black", linewidth=0.8)

    ax.set_title(
        "PIB per capita por país — 2024",
        fontsize=14,
        fontweight="bold",
        pad=15,
    )
    ax.set_ylabel("PIB per capita (US$ correntes)", fontsize=11)
    ax.yaxis.set_major_formatter(
        mticker.FuncFormatter(lambda x, _: f"US$ {x:,.0f}")
    )

    for bar in bars:
        height = bar.get_height()
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            height,
            f"US$ {int(height):,}",
            ha="center",
            va="bottom",
            fontsize=9,
        )

    ax.tick_params(axis="x", labelrotation=45)
    ax.grid(axis="y", linestyle="--", alpha=0.4)
    sns.despine(ax=ax)
    plt.tight_layout()
    plt.savefig(output_file, dpi=CHART_DPI, bbox_inches="tight")
    plt.close()
    logger.info(f"Bar chart saved to {output_file}")


def generate_choropleth_map(output_file):
    logger.info("Generating choropleth map...")

    # Ensure GeoJSON is available
    if not GEOJSON_PATH.exists():
        download_geojson(GEOJSON_URL, GEOJSON_PATH)

    try:
        gdf = gpd.read_file(GEOJSON_PATH)
    except Exception as e:
        logger.error(f"Failed to read GeoJSON: {e}")
        raise

    gdf = gdf.rename(columns={"ISO3166-1-Alpha-3": "ISO3"})
    gdf = gdf[gdf["ISO3"].isin(list(COUNTRY_METADATA.keys()))].copy()

    gdf["Nome"] = gdf["ISO3"].map(lambda x: COUNTRY_METADATA[x].name)
    gdf["Cor"] = gdf["ISO3"].map(lambda x: COUNTRY_METADATA[x].color)
    gdf = gdf.to_crs("EPSG:3857")

    fig, ax = plt.subplots(figsize=(10, 12))

    for _, row in gdf.iterrows():
        gpd.GeoDataFrame([row], crs=gdf.crs).plot(
            ax=ax, color=row["Cor"], edgecolor="white", linewidth=1
        )

    for _, row in gdf.iterrows():
        c = row.geometry.centroid
        ax.annotate(
            row["Nome"],
            xy=(c.x, c.y),
            ha="center",
            va="center",
            fontsize=8,
            fontweight="bold",
            color="#111111",
        )

    legend_patches = [
        mpatches.Patch(color=COUNTRY_METADATA[iso].color, label=COUNTRY_METADATA[iso].name)
        for iso in COUNTRIES_WITH_TIMESERIES
    ]
    ax.legend(
        handles=legend_patches,
        title="Países com série histórica",
        loc="lower left",
        fontsize=9,
        title_fontsize=10,
    )

    ax.set_title(
        "PIB per capita — América do Sul (2024)",
        fontsize=14,
        fontweight="bold",
        pad=15,
    )
    ax.axis("off")
    plt.tight_layout()
    plt.savefig(output_file, dpi=CHART_DPI, bbox_inches="tight")
    plt.close()
    logger.info(f"Choropleth map saved to {output_file}")


def main():
    try:
        Path(OUTPUT_DIR).mkdir(exist_ok=True)

        df = load_data(DATA_FILE)
        validate_countries(df)

        timeseries_data, years = prepare_timeseries_data(df)
        data_2024 = prepare_2024_data(df)

        generate_line_chart(timeseries_data, years, Path(OUTPUT_DIR) / "grafico1_linha.png")
        generate_bar_chart(data_2024, Path(OUTPUT_DIR) / "grafico2_barras.png")
        generate_choropleth_map(Path(OUTPUT_DIR) / "grafico3_coropleto.png")

        logger.info("All charts generated successfully!")

    except FileNotFoundError as e:
        logger.error(f"File error: {e}")
        sys.exit(1)
    except requests.RequestException as e:
        logger.error(f"Network error: {e}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
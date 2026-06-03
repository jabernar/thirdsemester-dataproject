# Visualização da Informação — PIB Per Capita América do Sul.
# Fonte: Banco Mundial — https://data.worldbank.org/indicator/NY.GDP.PCAP.CD

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import matplotlib.patches as mpatches
import seaborn as sns
import geopandas as gpd
import requests
import os

ANOS = list(range(2014, 2025))

dados_pib = {
    "Brasil":    [12070, 8757, 8727, 9895, 9001, 8717, 7741, 7519, 10413, 10378, 10280],
    "Chile":     [14629, 13572, 13576, 15073, 15923, 14898, 12975, 16265, 16104, 16490, 16710],
    "Argentina": [12973, 13791, 12790, 14398, 11653,  9888,  8442, 10636, 13738, 13326, 13858],
    "Colômbia":  [ 7903,  6098,  5806,  6378,  6651,  6432,  5333,  6104,  7040,  7060,  7914],
    "Peru":      [ 6541,  6121,  6197,  6762,  7032,  7171,  6144,  6712,  7126,  7323,  8452],
    "Uruguai":   [16810, 15623, 15565, 16681, 17274, 16190, 15437, 16652, 19799, 22168, 23907],
}

pib_2024 = {
    "URY": 23907, "CHL": 16710, "ARG": 13858, "BRA": 10280,
    "GUY":  9548, "PER":  8452, "COL":  7914, "SUR":  7431,
    "ECU":  6875, "PRY":  6416, "VEN":  4511, "BOL":  3939,
}

nomes_pt = {
    "URY": "Uruguai",   "CHL": "Chile",     "ARG": "Argentina",
    "BRA": "Brasil",    "GUY": "Guiana",    "PER": "Peru",
    "COL": "Colômbia",  "SUR": "Suriname",  "ECU": "Equador",
    "PRY": "Paraguai",  "VEN": "Venezuela", "BOL": "Bolívia",
}

paleta = sns.color_palette("tab10", 6)
cores_paises = {pais: paleta[i] for i, pais in enumerate(dados_pib.keys())}

cores_mapa = {
    "BRA": "#1f77b4", "CHL": "#ff7f0e", "ARG": "#2ca02c",
    "COL": "#d62728", "PER": "#9467bd", "URY": "#8c564b",
    "GUY": "#aec7e8", "SUR": "#c5b0d5", "ECU": "#ffbb78",
    "PRY": "#98df8a", "VEN": "#ff9896", "BOL": "#c49c94",
}

# PIB per capita ao longo do tempo 

print("Gerando gráfico 1 — Linha...")

fig, ax = plt.subplots(figsize=(10, 5))
for pais, valores in dados_pib.items():
    ax.plot(ANOS, valores, marker="o", markersize=4, linewidth=2,
            label=pais, color=cores_paises[pais])

ax.set_title("PIB per capita — América do Sul (2014–2024)", fontsize=13, pad=10)
ax.set_xlabel("Ano")
ax.set_ylabel("PIB per capita (US$ correntes)")
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"US$ {x:,.0f}"))
ax.set_xticks(ANOS)
ax.tick_params(axis="x", labelrotation=45)
ax.legend(bbox_to_anchor=(1.01, 1), loc="upper left", fontsize=9)
ax.grid(axis="y", linestyle="--", alpha=0.4)
sns.despine(ax=ax)
plt.tight_layout()
plt.savefig("grafico1_linha.png", dpi=150, bbox_inches="tight")
plt.close()

# Participação relativa em 2024

print("Gerando gráfico 2 — Setores...")

valores_2024 = {pais: valores[-1] for pais, valores in dados_pib.items()}

fig, ax = plt.subplots(figsize=(7, 7))
wedges, texts, autotexts = ax.pie(
    valores_2024.values(),
    labels=valores_2024.keys(),
    autopct="%1.1f%%",
    startangle=140,
    pctdistance=0.80,
    wedgeprops={"linewidth": 0.6, "edgecolor": "white"},
    colors=paleta,
)
for at in autotexts:
    at.set_fontsize(9)
ax.set_title("Participação relativa no PIB per capita\nAmérica do Sul — 2024", fontsize=13, pad=14)
plt.tight_layout()
plt.savefig("grafico2_setores.png", dpi=150, bbox_inches="tight")
plt.close()

# Mapa da América do Sul por PIB em 2024

GEOJSON_PATH = "/tmp/countries.geojson"
if not os.path.exists(GEOJSON_PATH):
    print("  Baixando GeoJSON...")
    r = requests.get(
        "https://raw.githubusercontent.com/datasets/geo-countries/master/data/countries.geojson",
        verify=False,
    )
    with open(GEOJSON_PATH, "w") as f:
        f.write(r.text)

gdf = gpd.read_file(GEOJSON_PATH)
gdf = gdf.rename(columns={"ISO3166-1-Alpha-3": "ISO3"})
gdf = gdf[gdf["ISO3"].isin(list(pib_2024.keys()))].copy()
gdf["PIB"] = gdf["ISO3"].map(pib_2024)
gdf["Nome"] = gdf["ISO3"].map(nomes_pt)
gdf["Cor"] = gdf["ISO3"].map(cores_mapa)
gdf = gdf.to_crs("EPSG:3857")

fig, ax = plt.subplots(figsize=(8, 10))
for _, row in gdf.iterrows():
    gpd.GeoDataFrame([row], crs=gdf.crs).plot(
        ax=ax, color=row["Cor"], edgecolor="white", linewidth=0.8,
    )
for _, row in gdf.iterrows():
    c = row.geometry.centroid
    ax.annotate(
        f"{row['Nome']}\nUS$ {row['PIB']:,.0f}",
        xy=(c.x, c.y), ha="center", va="center", fontsize=6, color="#111111",
    )

paises_pizza = ["URY", "CHL", "ARG", "BRA", "COL", "PER"]
legendas = [
    mpatches.Patch(color=cores_mapa[iso], label=nomes_pt[iso])
    for iso in paises_pizza
]
ax.legend(handles=legendas, title="Países (mesmas cores\ndo gráfico de setores)",
          loc="lower left", fontsize=8, title_fontsize=8)
ax.set_title("PIB per capita — América do Sul (2024)", fontsize=14, pad=12)
ax.axis("off")
plt.tight_layout()
plt.savefig("grafico3_coropleto.png", dpi=150, bbox_inches="tight")
plt.close()
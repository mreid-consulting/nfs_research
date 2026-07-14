import json
import numpy as np
import pandas as pd
import geopandas as gpd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm
from matplotlib.cm import ScalarMappable
import contextily as cx
from pyproj import Transformer

from src.paths import REPO_ROOT, DATA_ROOT
ROOT = str(REPO_ROOT)
SCRATCH = str(REPO_ROOT / "src" / "viz")
FIG = f"{ROOT}/results/london_pilot/figures"
REPO_ROOT.joinpath("results/london_pilot/figures").mkdir(parents=True, exist_ok=True)

df = pd.read_parquet(f"{DATA_ROOT}/data/processed/london_map_cells.parquet")
boroughs = gpd.read_file(f"{SCRATCH}/london_boroughs_3857.gpkg")

tr = Transformer.from_crs("EPSG:27700", "EPSG:3857", always_xy=True)

def to_3857(sub):
    x, y = tr.transform(sub["e50"].to_numpy(), sub["n50"].to_numpy())
    return x, y

pol = df[df.selected_policy].copy()
tru = df[df.selected_truth].copy()
pol["x"], pol["y"] = to_3857(pol)
tru["x"], tru["y"] = to_3857(tru)
pol["rate_per1000"] = pol["lambda_eb_tr"] * 1000
tru["rate_per1000"] = tru["test_rate"] * 1000

vmin = min(pol["rate_per1000"].min(), tru["rate_per1000"].min())
vmax = float(np.percentile(tru["rate_per1000"], 99))
norm = LogNorm(vmin=max(vmin, 0.5), vmax=vmax)
cmap = plt.get_cmap("YlOrRd")

cxr, cyr = np.load(f"{SCRATCH}/inset_center.npy")
HALF = 4200  # metres, densest-selection inner London window
MINX, MAXX = cxr - HALF, cxr + HALF
MINY, MAXY = cyr - HALF, cyr + HALF

def draw_panel(ax, sub, title, size_col="d"):
    boroughs.boundary.plot(ax=ax, color="#555555", linewidth=0.7, zorder=2)
    sizes = 20 + 90 * (sub[size_col] / sub[size_col].max())
    ax.scatter(sub["x"], sub["y"], c=sub["rate_per1000"], s=sizes, cmap=cmap, norm=norm,
               alpha=0.85, linewidths=0.3, edgecolors="white", zorder=3)
    ax.set_xlim(MINX, MAXX)
    ax.set_ylim(MINY, MAXY)
    ax.set_aspect("equal")
    ax.set_xticks([]); ax.set_yticks([])
    for s in ax.spines.values():
        s.set_visible(False)
    ax.set_title(title, fontsize=10.5, fontweight="bold", pad=6)
    try:
        cx.add_basemap(ax, source=cx.providers.CartoDB.Positron, crs="EPSG:3857",
                        zorder=1, attribution="")
        basemap_ok = True
    except Exception as e:
        print("basemap failed:", repr(e))
        ax.set_facecolor("#f0efe9")
        basemap_ok = False
    return basemap_ok

fig = plt.figure(figsize=(11, 6.4))
gs = fig.add_gridspec(2, 2, height_ratios=[1, 0.05], hspace=0.35, wspace=0.03,
                       top=0.86, bottom=0.155, left=0.01, right=0.99)
ax1 = fig.add_subplot(gs[0, 0]); ax2 = fig.add_subplot(gs[0, 1])
cax = fig.add_subplot(gs[1, :])

ok1 = draw_panel(ax1, pol, "Policy (inset): 2009–2020 EB-shrunk\ntargeting, densest selection area")
ok2 = draw_panel(ax2, tru, "Out-of-sample (inset): realised\n2021–2024 concentration, same area")

sm = ScalarMappable(norm=norm, cmap=cmap)
sm.set_array([])
cbar = fig.colorbar(sm, cax=cax, orientation="horizontal", extend="max")
cbar.set_label("dwelling fires per 1,000 dwelling-years (log scale)  ·  left: EB-shrunk 2009–20 rate  ·  right: realised 2021–24 rate (capped at truth-panel 99th pct)",
               fontsize=7.6)
cbar.ax.tick_params(labelsize=7.5)

attrib = ("Basemap © CARTO, © OpenStreetMap contributors  ·  grey outlines: London boroughs  ·  "
          "point size ∝ cell dwelling count  ·  ~8.4 km × 8.4 km window centred on inner south London (Southwark/Lambeth)")
fig.text(0.5, 0.012, attrib, ha="center", fontsize=6.6, color="#555555")
fig.suptitle("Inset: densest part of the 10,000-visit targeting budget", fontsize=12.5, y=0.975)

for e in ("png", "pdf"):
    fig.savefig(f"{FIG}/fig_map_targeting_inset.{e}", dpi=300)
plt.close(fig)
print("wrote fig_map_targeting_inset.png/pdf  basemap_ok=", ok1, ok2)
print("n cells policy in inset:", len(pol[(pol.x.between(MINX,MAXX)) & (pol.y.between(MINY,MAXY))]))
print("n cells truth in inset:", len(tru[(tru.x.between(MINX,MAXX)) & (tru.y.between(MINY,MAXY))]))

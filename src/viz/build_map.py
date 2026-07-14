import json
import numpy as np
import pandas as pd
import geopandas as gpd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import Normalize
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

# shared colour scale: EB rate (policy) and realised test rate (truth), per
# 1,000 dwelling-years, log-scaled since both are heavily right-skewed
pol["rate_per1000"] = pol["lambda_eb_tr"] * 1000
tru["rate_per1000"] = tru["test_rate"] * 1000
vmin = min(pol["rate_per1000"].min(), tru["rate_per1000"].min())
# cap the top of the shared scale at the 99th pct of the (noisier) truth panel
# so a handful of small-denominator outlier cells don't crush the dynamic
# range; values above are shown at the top colour with a colorbar "over" arrow.
vmax = float(np.percentile(tru["rate_per1000"], 99))
from matplotlib.colors import LogNorm
norm = LogNorm(vmin=max(vmin, 0.5), vmax=vmax)
cmap = plt.get_cmap("YlOrRd")

MINX, MINY, MAXX, MAXY = boroughs.total_bounds
PAD = 1500

def draw_panel(ax, sub, title, size_col="d"):
    boroughs.boundary.plot(ax=ax, color="#555555", linewidth=0.45, zorder=2)
    sizes = 7 + 26 * (sub[size_col] / sub[size_col].max())
    ax.scatter(sub["x"], sub["y"], c=sub["rate_per1000"], s=sizes, cmap=cmap, norm=norm,
               alpha=0.8, linewidths=0, zorder=3)
    ax.set_xlim(MINX - PAD, MAXX + PAD)
    ax.set_ylim(MINY - PAD, MAXY + PAD)
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

ok1 = draw_panel(ax1, pol, "Policy: 10,000 visits targeted on\n2009–2020 EB-shrunk cell rate")
ok2 = draw_panel(ax2, tru, "Out-of-sample: realised 2021–2024\nfire concentration, same 10,000-visit budget")

sm = ScalarMappable(norm=norm, cmap=cmap)
sm.set_array([])
cbar = fig.colorbar(sm, cax=cax, orientation="horizontal", extend="max")
cbar.set_label("dwelling fires per 1,000 dwelling-years (log scale)  ·  left: EB-shrunk 2009–20 rate  ·  right: realised 2021–24 rate (capped at truth-panel 99th pct)",
               fontsize=7.6)
cbar.ax.tick_params(labelsize=7.5)

attrib = "Basemap © CARTO, © OpenStreetMap contributors  ·  grey outlines: London boroughs  ·  point size ∝ cell dwelling count" if (ok1 or ok2) else "Basemap unavailable (offline) — boundary-only fallback  ·  grey outlines: London boroughs"
fig.text(0.5, 0.012, attrib, ha="center", fontsize=6.8, color="#555555")
fig.suptitle("Where the 10,000-visit London targeting budget goes", fontsize=12.5, y=0.975)

for e in ("png", "pdf"):
    fig.savefig(f"{FIG}/fig_map_targeting.{e}", dpi=300)
plt.close(fig)
print("wrote fig_map_targeting.png/pdf  basemap_ok=", ok1, ok2)

meta = {"basemap_ok": bool(ok1 and ok2), "vmin": float(norm.vmin), "vmax": float(norm.vmax)}
with open(f"{SCRATCH}/map_meta.json", "w") as fh:
    json.dump(meta, fh, indent=2)

"""2x2 targeting map: rows = window (in-sample 2009-20 / out-of-sample
2021-24), columns = estimator (EB-shrunk / realised raw), on the SAME 1,948
policy-selected cells throughout. inset=True crops to the densest cluster."""
import sys
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

INSET = "--inset" in sys.argv

df = pd.read_parquet(f"{DATA_ROOT}/data/processed/london_map_cells.parquet")
boroughs = gpd.read_file(f"{SCRATCH}/london_boroughs_3857.gpkg")

tr = Transformer.from_crs("EPSG:27700", "EPSG:3857", always_xy=True)
pol = df[df.selected_policy].copy()
pol["x"], pol["y"] = tr.transform(pol["e50"].to_numpy(), pol["n50"].to_numpy())

GREY = "#c9c9c9"  # distinct colour for cells with zero fires in that window

panels = [
    ("eb_rate_0920",  "EB-shrunk estimate",  "In-sample 2009–20"),
    ("raw_rate_0920", "Realised raw rate",   "In-sample 2009–20"),
    ("eb_rate_2124",  "EB-shrunk estimate",  "Out-of-sample 2021–24"),
    ("raw_rate_2124", "Realised raw rate",   "Out-of-sample 2021–24"),
]
for col, *_ in panels:
    pol[col + "_per1000"] = pol[col] * 1000

# shared colour scale across all 4 panels: floored at a fixed low value and
# capped at a high percentile of the noisiest panel (realised raw,
# out-of-sample). The EB estimate for cells in an LSOA with literally zero
# 2021-24 fires collapses towards the eb_shrink() numerical floor (~1e-9,
# from its internal lambda_i clip(1e-12)) -- a handful of such cells (66 of
# 1,948) would otherwise stretch the scale over 9 decades and wash out every
# other panel. clip=True draws anything below vmin at the palest colour
# (reads as "near zero", same story as the grey realised-zero cells) without
# distorting the shared range. vmin matches the natural floor of the raw-rate
# panels (~8-30/1000) so the estimate columns stay visually comparable.
vmin = 5.0
vmax = float(np.percentile(pol["raw_rate_2124_per1000"][pol["raw_rate_2124_per1000"] > 0], 99))
norm = LogNorm(vmin=vmin, vmax=vmax, clip=True)
cmap = plt.get_cmap("YlOrRd")

if INSET:
    cxr, cyr = np.load(f"{SCRATCH}/inset_center.npy")
    HALF = 4200
    MINX, MAXX = cxr - HALF, cxr + HALF
    MINY, MAXY = cyr - HALF, cyr + HALF
    figsize = (10.6, 11.6)
    out_base = "fig_map_targeting_inset"
    size_lo, size_hi = 20, 110
    lw_border = 0.7
else:
    MINX, MINY, MAXX, MAXY = boroughs.total_bounds
    PAD = 1500
    MINX -= PAD; MAXX += PAD; MINY -= PAD; MAXY += PAD
    figsize = (10.6, 12.2)
    out_base = "fig_map_targeting"
    size_lo, size_hi = 5, 24
    lw_border = 0.45

def draw_panel(ax, col, title):
    boroughs.boundary.plot(ax=ax, color="#555555", linewidth=lw_border, zorder=2)
    vals = pol[col + "_per1000"]
    zero = vals <= 0
    sizes = size_lo + (size_hi - size_lo) * (pol["d"] / pol["d"].max())
    if zero.any():
        ax.scatter(pol.loc[zero, "x"], pol.loc[zero, "y"], c=GREY, s=sizes[zero],
                   alpha=0.85, linewidths=0.2, edgecolors="white" if INSET else "none", zorder=3)
    ax.scatter(pol.loc[~zero, "x"], pol.loc[~zero, "y"], c=vals[~zero], s=sizes[~zero],
               cmap=cmap, norm=norm, alpha=0.85, linewidths=0.2,
               edgecolors="white" if INSET else "none", zorder=4)
    ax.set_xlim(MINX, MAXX); ax.set_ylim(MINY, MAXY)
    ax.set_aspect("equal"); ax.set_xticks([]); ax.set_yticks([])
    for s in ax.spines.values():
        s.set_visible(False)
    ax.set_title(title, fontsize=9.5, fontweight="bold", pad=5)
    try:
        cx.add_basemap(ax, source=cx.providers.CartoDB.Positron, crs="EPSG:3857",
                        zorder=1, attribution="")
        ok = True
    except Exception as e:
        print("basemap failed:", repr(e))
        ax.set_facecolor("#f0efe9")
        ok = False
    return ok

fig = plt.figure(figsize=figsize)
gs = fig.add_gridspec(4, 2, height_ratios=[0.09, 1, 1, 0.045], hspace=0.28, wspace=0.03,
                       top=0.93, bottom=0.095, left=0.03, right=0.99)
ax_hdr = fig.add_subplot(gs[0, :]); ax_hdr.axis("off")
ax_ee = fig.add_subplot(gs[1, 0]); ax_re = fig.add_subplot(gs[1, 1])
ax_eo = fig.add_subplot(gs[2, 0]); ax_ro = fig.add_subplot(gs[2, 1])
cax = fig.add_subplot(gs[3, :])

# column headers (once, above the top row)
ax_hdr.text(0.27, 0.15, "ESTIMATE  (EB-shrunk, Gamma–Poisson)", ha="center", va="bottom",
            fontsize=10.5, fontweight="bold", transform=ax_hdr.transAxes)
ax_hdr.text(0.77, 0.15, "REALISED  (raw counted rate)", ha="center", va="bottom",
            fontsize=10.5, fontweight="bold", transform=ax_hdr.transAxes)

oks = []
oks.append(draw_panel(ax_ee, "eb_rate_0920", "In-sample 2009–20 · EB-shrunk estimate\n(the ranking the policy acts on)"))
oks.append(draw_panel(ax_re, "raw_rate_0920", "In-sample 2009–20 · realised raw rate"))
oks.append(draw_panel(ax_eo, "eb_rate_2124", "Out-of-sample 2021–24 · EB-shrunk estimate\n(same machinery, held-out counts)"))
oks.append(draw_panel(ax_ro, "raw_rate_2124", "Out-of-sample 2021–24 · realised raw rate"))

# row labels, rotated, to the left of each row
for ax, lbl in [(ax_ee, "IN-SAMPLE\n2009–20"), (ax_eo, "OUT-OF-SAMPLE\n2021–24")]:
    ax.annotate(lbl, xy=(0, 0.5), xytext=(-14, 0), xycoords="axes fraction",
                textcoords="offset points", ha="right", va="center", fontsize=8.5,
                fontweight="bold", rotation=90, color="#333333")

sm = ScalarMappable(norm=norm, cmap=cmap)
sm.set_array([])
cbar = fig.colorbar(sm, cax=cax, orientation="horizontal", extend="max")
cbar.set_label("dwelling fires per 1,000 dwelling-years (log scale)", fontsize=8.5)
cbar.ax.tick_params(labelsize=7.5)

basemap_ok = all(oks)
note1a = f"Grey = zero realised fires in that window (n={int((pol['raw_rate_2124']<=0).sum())} of {len(pol)} cells, out-of-sample panel)."
note1b = "Palest colour = at/below the scale floor (incl. EB estimates for cells in zero-fire LSOAs); scale floored at 5, capped at the realised-panel 99th pct."
attrib = ("Basemap © CARTO, © OpenStreetMap contributors  ·  grey outlines: London boroughs  ·  "
          "point size ∝ cell dwelling count  ·  same 1,948 policy-selected cells in all four panels"
          + ("" if basemap_ok else "  ·  basemap unavailable offline — boundary-only fallback"))
fig.text(0.5, 0.038, note1a, ha="center", fontsize=6.8, color="#444444")
fig.text(0.5, 0.024, note1b, ha="center", fontsize=6.8, color="#444444")
fig.text(0.5, 0.006, attrib, ha="center", fontsize=6.4, color="#555555")

title = ("Estimate vs realised: the 10,000-visit policy selection, in-sample and out-of-sample"
         if not INSET else
         "Estimate vs realised (inset, densest selection area): in-sample and out-of-sample")
fig.suptitle(title, fontsize=12.5, y=0.985)

for e in ("png", "pdf"):
    fig.savefig(f"{FIG}/{out_base}.{e}", dpi=300)
plt.close(fig)
print(f"wrote {out_base}.png/pdf  basemap_ok=", oks)

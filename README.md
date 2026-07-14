# nfs_research — papers and chart production for the UK residential fire-risk work

The **research layer**: the two papers (LaTeX) and the code that turns the outputs
of the data and analysis repositories into paper figures and tables.

## Contents

| Path | What it is |
|---|---|
| `paper/`, `paper2/` | The two papers — LaTeX sources and committed figures; each builds standalone with `latexmk -pdf main.tex` |
| `src/viz/` | Chart production — London targeting maps and borough table, from the sub-LSOA grid (data + analysis output) |
| `src/paths.py` | Resolves the `nfs_data` and `nfs_analysis` dependencies |
| `REPRODUCE.md` | Section-by-section commands mapping each paper result to the script that produces it |

## Dependencies

- **nfs_data** — the aggregated database and the sub-LSOA London grid. `NFS_DATA`
  env var, default sibling `../nfs_data`.
- **nfs_analysis** — the models and their `results/`. `NFS_ANALYSIS` env var,
  default sibling `../nfs_analysis`.

```bash
# alongside this repo:
#   ../nfs_data      (git lfs pull && ./setup.sh)
#   ../nfs_analysis
python -m venv .venv && . .venv/bin/activate
pip install -r requirements.txt   # shared pinned env; this layer uses the plotting/geo subset
./setup.sh                        # verifies both dependencies are reachable
```

## Build the papers

```bash
latexmk -pdf paper/main.tex
latexmk -pdf paper2/main.tex
```

## Regenerate the London charts

```bash
python -m src.viz.build_map        # main targeting map
python -m src.viz.build_map_2x2    # 4-panel EB-vs-realised, in/out of sample
python -m src.viz.build_borough_table
```

Figures produced by the analysis modules themselves (calibration curves, forest
plots, the Morris screening) live under `nfs_analysis/results/`; the committed
copies in `paper/figures/` and `paper2/figures/` are what the papers include.

# Reproducing both papers

Everything in `paper/main.pdf` (paper 1) and `paper2/main.pdf` (paper 2) traces
to a results file, which traces to code, which reads the aggregated database.
This document is the end-to-end map. All model runs use fixed seeds (stated per
module and per results summary).

## Repository layout — which repo runs what

The work spans **three sibling repositories**. Clone all three side by side and
set up `nfs_data` first (it ships the database via git-LFS):

```
nfs_data/       # data layer — run:  src.ingest.*, src.build_db, src.validate
nfs_analysis/   # models      — run:  src.models.*, src.physics.*, src.sim.*
nfs_research/   # this repo    — run: src.viz.*, and the paper builds (latexmk)
```

- Commands below prefixed `src.ingest` / `src.build_db` / `src.validate` are run
  **in `nfs_data`** (§1–§2).
- Commands prefixed `src.models` / `src.physics` / `src.sim` are run **in
  `nfs_analysis`** (§3–§5); they read the database from `nfs_data` and write model
  outputs to `nfs_analysis/results/`. `nfs_analysis` locates `nfs_data` via the
  `NFS_DATA` env var (default sibling `../nfs_data`).
- Commands prefixed `src.viz`, and the `latexmk` paper builds, are run **here in
  `nfs_research`**; `src.paths` locates the other two via `NFS_DATA` /
  `NFS_ANALYSIS` (default siblings).
- Paths like `data/processed/…` and `results/…` in the tables below are relative
  to the repo that owns that command.

The static figures the papers `\includegraphics` are committed under
`paper/figures/` and `paper2/figures/`; re-running an analysis module refreshes
its figure under `nfs_analysis/results/`, which you then copy into `paper/figures/`.

## 0. Environment

- Python 3.12, `python3 -m venv .venv`, then
  `./.venv/bin/pip install -r requirements.txt` (exact frozen versions).
- LaTeX (`pdflatex` + `bibtex`) for the papers.
- For the physics engine only: `gfortran` (Homebrew gcc) to build NIST CFAST
  from source — see §5.
- Hardware note: all fits run on CPU (Apple Silicon used originally). NUTS
  subsample fits take minutes–hours; the CFAST sweep took ~3.5 h at 9-way
  parallelism.

## 1. Raw data (`data/raw/`, ~14 GB, ships with the repo distribution)

Every source's URL, licence, retrieval date, and schema is documented in
`data/sources/*.md`. Re-download notes:

| Source | Re-downloadable? | Script / route |
|---|---|---|
| MHCLG incident-level + FIRE tables | yes, public URLs | documented in `data/sources/incidents.md`, `fire_tables_catalogue.md` |
| EPC domestic bulk (6.5 GB zip) | yes, but needs a free API key (GOV.UK One Login) and the file is rebuilt daily — ours is pinned (lastUpdated 2026-07-03) | `src/ingest/epc_download.py` (key via `EPC_API_KEY`) |
| IMD 2025, Census 2021, CQC, ONSUD, OS Open UPRN, LSOA boundaries, postcode lookup | yes, public | URLs in `data/sources/buildings.md` |
| LFB incident records | yes, public (updated monthly; ours pinned) | URLs in `data/sources/lfb.md` |
| Camden FRA corpus (1,441 PDFs) | portal overwrites PDFs in place — our snapshot is **not** re-downloadable as-was | harvested with `data/raw/fra/camden/{harvest_index,download_pdfs}.py`; the PDFs are archival (shipped with `data/raw/`), but the **extracted datasets are tracked in git** (`data/processed/fra/*.csv`, `panel*.parquet`, the index and wave-0 date pairs) precisely because they cannot be regenerated from any download — all latent-state analyses reproduce from git alone |
| Wave-0 archived FRAs (10 PDFs) | pinned Wayback URLs | `data/raw/fra/camden_wave0/manifest.json` |

## 2. Database (both papers)

The built database ships in git via LFS as two attachable files (GitHub's
2 GiB/file cap): `data/processed/fire_risk_core.duckdb` (all 76 tables + views,
everything the analyses read) and `fire_risk_lookups.duckdb` (the two large
open UPRN reference tables; `ATTACH` when needed). To rebuild from raw instead:

```bash
./.venv/bin/python -m src.build_db --with-epc --with-lfb   # raw -> data/processed/fire_risk.duckdb
./.venv/bin/python -m src.validate                          # 28 automated checks -> data/processed/VALIDATION.md
```

Schema and join keys: `data/processed/SCHEMA.md`. Flags are preserve-if-absent:
a run without `--with-epc`/`--with-lfb` never drops those tables.

## 3. Paper 1 results, section by section

| Paper 1 section | Command(s) | Output consumed by the paper |
|---|---|---|
| Occurrence model + calibration | `python -m src.models.run_occurrence fit` then `eval`; full-data ADVI: `fit_full` variant inside the module | `results/occurrence/summary.md`, figures |
| Ablation ladder, BYM2 spatial, subgroups | `python -m src.models.spatial_ablation fit` then `eval` | `results/occurrence/` (`_v2` artefacts, `ladder.log`) |
| Consequence models (+ response-time refit, full-data ADVI, proper scores, subgroups) | `python -m src.models.consequence` (`--full-fit` for the ADVI pass) | `results/consequence/summary.md` |
| Interactions (alarm×occupancy, night×dwelling) | `python -m src.models.interactions` | `results/interactions/summary.md` |
| Ignition-source trends | `python -m src.models.ignition_trends` | `results/ignition_trends/summary.md` |
| Simulation + surrogate | `python -m src.sim.run_experiments --runs 10000 --jobs 8 && python -m src.sim.surrogate && python -m src.sim.make_report` | `results/sim/summary.md` |
| Decision layer (policies, EVI, budget sweep, decision curves) | `python -m src.models.decision` | `results/decision/summary.md` |
| Grenfell case study + hindcast | `python -m src.sim.case_study && python -m src.sim.hindcast && python -m src.sim.make_case_figures` | `results/case_study/summary.md` |
| FRA latent-state instantiation | `python src/ingest/fra_extract.py && python src/ingest/fra_items.py && python -m src.ingest.fra_panel && python src/models/latent_state.py run` | `results/latent_state/summary.md`, `data/processed/fra/` |
| Two-wave pilot | `python src/models/two_wave_pairs.py` | `results/latent_state/two_wave_pairs.md` |
| London concentration paragraph | see paper 2 row 1 below | `results/london_pilot/summary.md` |

## 4. Paper 2 results, section by section

| Paper 2 section | Command(s) | Output |
|---|---|---|
| §2 sub-LSOA concentration + targeting | `python -m src.models.london_pilot` | `results/london_pilot/summary.md`, figures |
| §2.4 borough table + 2×2 maps | `python src/viz/build_borough_table.py && python src/viz/build_map_2x2.py && python src/viz/build_map_inset.py` (selection data: `data/processed/london_map_cells.parquet`; basemap tiles fetched live from CARTO/OSM) | `results/london_pilot/borough_allocation.csv`, `figures/fig_map_targeting*` |
| §3 building-level care-home model | inside `src.models.london_pilot` (analysis B) | `results/london_pilot/summary.md` |
| §4 CFAST engine (Phase A) | build CFAST (§5), then `python -m src.physics.mc_smoke_test` | `results/physics/phaseA_report.md` |
| §5 calibration (Phase B) | `python -m src.physics.sweep` (hours), `python -m src.physics.emulator`, `python -m src.physics.calibrate`, `python -m src.physics.phaseB_analysis`; side items `python -m src.physics.stair_bias`, `python -m src.physics.mech_vent` | `results/physics/phaseB_report.md`, `calibration/posterior.nc` |

## 5. Building CFAST (paper 2 physics only)

```bash
git clone --depth 1 https://github.com/firemodels/cfast.git vendor/cfast
cd vendor/cfast && git checkout 611ac4ab7   # the commit used throughout
cd Build/CFAST/gnu_osx && bash make_cfast.sh  # gfortran; other platforms: use the matching Build/ target
```

Verify against the shipped `Verification/NRC_Users_Guide/G_Transient_Fire_in_Corridor`
case before trusting outputs (`results/physics/phaseA_report.md` §1 documents the
expected result). `vendor/` is not tracked in git; the commit hash above pins it.

## 5b. Tests

```bash
./.venv/bin/python -m pytest tests/ -q   # unit tests (evacuation re-routing invariants)
```

## 6. Papers

```bash
cd paper  && pdflatex main && bibtex main && pdflatex main && pdflatex main
cd paper2 && pdflatex main && bibtex main && pdflatex main && pdflatex main
```

Figures used by the papers are copied into `paper*/figures/` from `results/`;
regenerating results regenerates them (re-copy when they change).

## 7. Known non-determinism and pinned-world caveats

- All samplers/Monte Carlo are seed-fixed; ADVI/NUTS results reproduce to
  reported precision on the same library versions (`requirements.txt`).
- The gradient-boosted emulator and map tiles introduce no seed randomness
  (emulator bootstraps are seeded), but basemap tiles are fetched live and may
  render cosmetically differently.
- Three sources are moving targets pinned by our snapshot: EPC bulk (daily
  rebuild), LFB records (monthly), Camden FRA portal (overwrites PDFs in
  place — our copy is the archival wave 1). Reproducing *from fresh downloads*
  will therefore differ slightly; reproducing from `data/raw/` as shipped is
  exact.
- Wall-clock: the two heavy steps are the CFAST sweep (~3.5 h at 9 workers)
  and full ADVI/NUTS fits (minutes–2 h each); everything else is minutes.

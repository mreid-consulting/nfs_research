import pandas as pd, numpy as np

from src.paths import REPO_ROOT, DATA_ROOT
ROOT = str(REPO_ROOT)
df = pd.read_parquet(f"{DATA_ROOT}/data/processed/london_map_cells.parquet")
pol = df[df.selected_policy].copy()
pol["borough_f"] = pol["borough"].fillna("Unmatched / boundary edge")
pol["visits"] = pol["d"] * pol["selected_policy_frac"]

BUDGET = 10000
g = pol.groupby("borough_f").apply(lambda x: pd.Series({
    "n_cells": len(x),
    "visits": x["visits"].sum(),
    "mean_eb_rate_per_1000dw_yr": np.average(x["lambda_eb_tr"], weights=x["visits"]) * 1000,
    "realised_2021_24_rate_per_1000dw_yr": np.average(x["test_rate"], weights=x["visits"]) * 1000,
}), include_groups=False).reset_index().rename(columns={"borough_f": "borough"})
g["pct_of_budget"] = 100 * g["visits"] / BUDGET
g = g.sort_values("pct_of_budget", ascending=False).reset_index(drop=True)

top = g.head(10).copy()
rest = g.iloc[10:]
if len(rest):
    rest_row = pd.DataFrame([{
        "borough": f"Rest ({len(rest)} boroughs)",
        "n_cells": rest["n_cells"].sum(),
        "visits": rest["visits"].sum(),
        "mean_eb_rate_per_1000dw_yr": np.average(rest["mean_eb_rate_per_1000dw_yr"], weights=rest["visits"]),
        "realised_2021_24_rate_per_1000dw_yr": np.average(rest["realised_2021_24_rate_per_1000dw_yr"], weights=rest["visits"]),
        "pct_of_budget": rest["pct_of_budget"].sum(),
    }])
    out = pd.concat([top, rest_row], ignore_index=True)
else:
    out = top

out = out[["borough", "n_cells", "visits", "pct_of_budget", "mean_eb_rate_per_1000dw_yr", "realised_2021_24_rate_per_1000dw_yr"]]
out["n_cells"] = out["n_cells"].round(0).astype(int)
out["visits"] = out["visits"].round(0).astype(int)
out["pct_of_budget"] = out["pct_of_budget"].round(1)
out["mean_eb_rate_per_1000dw_yr"] = out["mean_eb_rate_per_1000dw_yr"].round(2)
out["realised_2021_24_rate_per_1000dw_yr"] = out["realised_2021_24_rate_per_1000dw_yr"].round(2)

out_path = f"{ROOT}/results/london_pilot/borough_allocation.csv"
REPO_ROOT.joinpath("results/london_pilot").mkdir(parents=True, exist_ok=True)
out.to_csv(out_path, index=False)
print(out.to_string(index=False))
print("n boroughs total:", g["borough"].nunique())
print("wrote", out_path)

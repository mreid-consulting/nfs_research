#!/usr/bin/env bash
# Reproduction setup: check the data and analysis dependencies are reachable.
# This repo holds the papers and the chart code that consumes their outputs.
#   nfs_data     — aggregated database (override with NFS_DATA;     default ../nfs_data)
#   nfs_analysis — model outputs under results/ (override with NFS_ANALYSIS; default ../nfs_analysis)
set -euo pipefail
cd "$(dirname "$0")"
DATA="${NFS_DATA:-../nfs_data}"
ANALYSIS="${NFS_ANALYSIS:-../nfs_analysis}"
miss=0
[ -d "$DATA" ]     || { echo "ERROR: nfs_data not found at '$DATA' (set NFS_DATA)."; miss=1; }
[ -d "$ANALYSIS" ] || { echo "ERROR: nfs_analysis not found at '$ANALYSIS' (set NFS_ANALYSIS)."; miss=1; }
[ "$miss" = 0 ] || exit 1
echo "OK: charts read data from $DATA and analysis outputs from $ANALYSIS"

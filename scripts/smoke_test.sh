#!/usr/bin/env bash
set -euo pipefail

# Quick sanity run (template)
python -m bayesfusionsdf.train --config configs/train.yaml --data_root ./data/<dataset_name>/processed --output_dir ./outputs/smoke_train
python -m bayesfusionsdf.eval  --config configs/eval.yaml  --checkpoint ./outputs/smoke_train/checkpoints/latest.pt --data_root ./data/<dataset_name>/processed --output_dir ./outputs/smoke_eval
echo "[OK] Smoke test finished (template)."

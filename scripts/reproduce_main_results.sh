#!/usr/bin/env bash
set -euo pipefail

# Replace these commands with those that reproduce your paper's main tables/figures.
python -m bayesfusionsdf.train --config configs/train.yaml --data_root ./data/<dataset_name>/processed --output_dir ./outputs/exp_main
python -m bayesfusionsdf.eval  --config configs/eval.yaml  --checkpoint ./outputs/exp_main/checkpoints/latest.pt --data_root ./data/<dataset_name>/processed --output_dir ./outputs/exp_main_eval

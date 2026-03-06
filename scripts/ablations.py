# Purpose: Run ablations (noise/anchoring/probes/NBV) and aggregate metrics
import argparse
import itertools
import os
import subprocess
import sys
from pathlib import Path

import yaml


def set_in(cfg, path, val):
    d = cfg
    for k in path[:-1]:
        d = d[k]
    d[path[-1]] = val


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--base_cfg", default="configs/ours.yaml")
    ap.add_argument("--nbv_cfg", default="configs/nbv.yaml")
    ap.add_argument("--out_root", default="outputs/ablations")
    args = ap.parse_args()

    out_root = Path(args.out_root)
    out_root.mkdir(parents=True, exist_ok=True)

    # Ensure subprocess uses same interpreter and can import src/ without editable install
    repo_root = Path(__file__).resolve().parents[1]
    src_path = repo_root / "src"
    env = os.environ.copy()
    env["PYTHONPATH"] = str(src_path) + os.pathsep + env.get("PYTHONPATH", "")

    toggles = list(itertools.product([False, True], [False, True], [8, 16, 32], [False, True]))

    for i, (hetero, anchor, probes, nbv) in enumerate(toggles):
        cfg = yaml.safe_load(open(args.base_cfg, "r", encoding="utf-8"))
        set_in(cfg, ["model", "heteroscedastic"], hetero)
        set_in(cfg, ["model", "use_anchor"], anchor)
        set_in(cfg, ["variance", "probes"], probes)

        run_dir = out_root / f"run_{i:03d}"
        cfg["output"]["out_dir"] = str(run_dir)
        run_dir.mkdir(parents=True, exist_ok=True)

        # Write configs for reproducibility
        tmp_cfg = out_root / f"cfg_{i:03d}.yaml"
        with open(tmp_cfg, "w", encoding="utf-8") as f:
            yaml.safe_dump(cfg, f, sort_keys=False)

        nbvc = yaml.safe_load(open(args.nbv_cfg, "r", encoding="utf-8"))
        nbvc["nbv"]["enabled"] = nbv
        tmp_nbv = out_root / f"nbv_{i:03d}.yaml"
        with open(tmp_nbv, "w", encoding="utf-8") as f:
            yaml.safe_dump(nbvc, f, sort_keys=False)

        # Log each run
        log_file = run_dir / "stdout_stderr.txt"
        cmd = [sys.executable, "scripts/run_ours.py", "-c", str(tmp_cfg), "--nbv", str(tmp_nbv)]
        print(f"[Ablation {i:03d}] hetero={hetero} anchor={anchor} probes={probes} nbv={nbv}")
        print("  CMD:", " ".join(cmd))

        with open(log_file, "w", encoding="utf-8") as lf:
            subprocess.check_call(cmd, env=env, stdout=lf, stderr=subprocess.STDOUT)

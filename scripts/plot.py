import argparse, glob, json, os
from pathlib import Path

import matplotlib.pyplot as plt


def safe_float(x, default=0.0):
    try:
        if x is None:
            return default
        return float(x)
    except Exception:
        return default


def get_solver_resid(rec):
    """
    Supports multiple log formats:
      - rec["solver"] is dict: {"resid": ...}
      - rec["solver"] is int/float (cg info code): resid may be in rec["resid"] or missing
    """
    s = rec.get("solver", None)
    if isinstance(s, dict):
        # prefer "resid", but accept "residual" too
        return safe_float(s.get("resid", s.get("residual", 0.0)), 0.0)
    # solver might just be CG info code (0 is success)
    return safe_float(rec.get("resid", 0.0), 0.0)


def get_active_N(rec):
    """
    Supports:
      - rec["grid"]["N"]
      - rec["grid_N"]
      - rec["N"]
    """
    g = rec.get("grid", None)
    if isinstance(g, dict) and "N" in g:
        return int(g["N"])
    if "grid_N" in rec:
        return int(rec["grid_N"])
    if "N" in rec:
        return int(rec["N"])
    return None


def read_jsonl(path):
    rows = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError:
                # ignore corrupted lines
                continue
    return rows


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--in", dest="in_root", default="outputs")
    ap.add_argument("--out", default=None, help="output directory for plots (default: <in_root>)")
    args = ap.parse_args()

    in_root = Path(args.in_root)
    out_dir = Path(args.out) if args.out else in_root
    out_dir.mkdir(parents=True, exist_ok=True)

    # collect all run.jsonl
    logs = sorted(in_root.glob("**/run.jsonl"))
    if not logs:
        print(f"[plot] No run.jsonl found under: {in_root}")
        raise SystemExit(1)

    # gather points from all ours runs
    xs, ys = [], []
    for lp in logs:
        rows = read_jsonl(lp)
        for r in rows:
            if r.get("mode") != "ours":
                continue
            N = get_active_N(r)
            if N is None:
                continue
            resid = get_solver_resid(r)
            xs.append(N)
            ys.append(resid)

    if not xs:
        print("[plot] No usable 'ours' entries found in logs (missing mode/grid/solver fields).")
        raise SystemExit(1)

    # plot
    plt.figure()
    plt.scatter(xs, ys, s=12)
    plt.xlabel("Active voxels (N)")
    plt.ylabel("CG residual (proxy)")
    plt.title("BayesFusion-SDF: residual vs active voxel count")
    out_path = out_dir / "resid_vs_N.png"
    plt.savefig(out_path, dpi=200, bbox_inches="tight")
    print("[plot] wrote:", out_path)

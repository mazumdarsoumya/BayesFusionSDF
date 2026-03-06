import argparse
import os
import json
from pathlib import Path

import yaml
from tqdm import tqdm

def load_yaml(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

def main():
    parser = argparse.ArgumentParser(description="Preprocess CO3D into repo-expected layout (template).")
    parser.add_argument("--raw_root", required=True, help="Path to CO3D raw files (downloaded by you).")
    parser.add_argument("--out_root", required=True, help="Output root for processed data.")
    parser.add_argument("--splits", required=True, help="configs/data/co3d.yaml")
    args = parser.parse_args()

    raw_root = Path(args.raw_root)
    out_root = Path(args.out_root)
    out_root.mkdir(parents=True, exist_ok=True)

    cfg = load_yaml(args.splits)

    # TODO: Implement real preprocessing
    # This template just creates expected folders.
    for split in ("train", "val", "test"):
        (out_root / split).mkdir(parents=True, exist_ok=True)

    meta = {
        "raw_root": str(raw_root.resolve()),
        "out_root": str(out_root.resolve()),
        "cfg": cfg,
        "note": "This is a template. Replace with real CO3D preprocessing code.",
    }
    with open(out_root / "preprocess_meta.json", "w", encoding="utf-8") as f:
        json.dump(meta, f, indent=2)

    for _ in tqdm(range(5), desc="preprocess"):
        pass

    print(f"[OK] Wrote processed layout to: {out_root}")

if __name__ == "__main__":
    main()

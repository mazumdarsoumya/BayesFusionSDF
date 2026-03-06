# Purpose: CLI to generate synthetic dataset
import argparse
from bayesfusion_sdf.synth import make_sphere_scene

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--n_frames", type=int, default=12)
    args = ap.parse_args()
    make_sphere_scene(f"{args.out}/scene0000", n_frames=args.n_frames)

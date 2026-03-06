# Purpose: CPU-friendly subsampling (frame stride + max frames)
import argparse, shutil
from pathlib import Path

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--in_root", required=True)
    ap.add_argument("--out_root", required=True)
    ap.add_argument("--stride", type=int, default=2)
    ap.add_argument("--max_frames", type=int, default=200)
    args = ap.parse_args()
    inp = Path(args.in_root); out = Path(args.out_root)
    for sub in ["depth","pose","intrinsic","gt"]:
        (out/sub).mkdir(parents=True, exist_ok=True)
    depth_files = sorted((inp/"depth").glob("*.png"))[:args.max_frames:args.stride]
    for df in depth_files:
        i = df.stem
        shutil.copy2(df, out/"depth"/df.name)
        shutil.copy2(inp/"pose"/f"{i}.txt", out/"pose"/f"{i}.txt")
    shutil.copy2(inp/"intrinsic"/"intrinsic.txt", out/"intrinsic"/"intrinsic.txt")
    if (inp/"gt").exists():
        for f in (inp/"gt").glob("*"):
            shutil.copy2(f, out/"gt"/f.name)

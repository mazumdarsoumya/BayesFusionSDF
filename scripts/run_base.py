# Purpose: Run TSDF baseline and save mesh/logs
import argparse, os
from bayesfusion_sdf.config import load_yaml
from bayesfusion_sdf.tsdf import integrate_tsdf
from bayesfusion_sdf.profiling import append_jsonl, thread_env
import open3d as o3d

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("-c","--config", required=True)
    args = ap.parse_args()
    cfg = load_yaml(args.config)
    out = cfg["output"]["out_dir"]
    os.makedirs(f"{out}/meshes", exist_ok=True)
    os.makedirs(f"{out}/logs", exist_ok=True)
    mesh = integrate_tsdf(cfg["data"]["root"], cfg["data"]["stride"], cfg["data"]["max_frames"],
                          cfg["tsdf"]["voxel"], cfg["tsdf"]["trunc"], cfg["data"]["depth_scale"])
    o3d.io.write_triangle_mesh(f"{out}/meshes/tsdf_mesh.ply", mesh)
    append_jsonl(f"{out}/logs/run.jsonl", {"mode":"baseline", "thread_env":thread_env(), "mesh":"meshes/tsdf_mesh.ply"})

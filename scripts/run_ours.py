# Purpose: Run BayesFusion-SDF (MAP+variance+optional NBV)
import argparse, os, numpy as np
import open3d as o3d
from bayesfusion_sdf.config import load_yaml, dump_yaml
from bayesfusion_sdf.tsdf import integrate_tsdf
from bayesfusion_sdf.core import build_grid_from_mesh, build_prior_laplacian, depth_points, build_data_diag, solve_map, hutchinson_diag, iso_points, plan_nbv
from bayesfusion_sdf.profiling import append_jsonl, thread_env

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("-c","--config", required=True)
    ap.add_argument("--nbv", default=None)
    args = ap.parse_args()
    cfg = load_yaml(args.config)
    nbv_cfg = load_yaml(args.nbv) if args.nbv else {"nbv":{"enabled":False}}
    out = cfg["output"]["out_dir"]
    os.makedirs(f"{out}/meshes", exist_ok=True)
    os.makedirs(f"{out}/metrics", exist_ok=True)
    os.makedirs(f"{out}/logs", exist_ok=True)

    mesh0 = integrate_tsdf(cfg["data"]["root"], cfg["data"]["stride"], cfg["data"]["max_frames"],
                           cfg["model"]["voxel"], cfg["model"]["band"], cfg["data"]["depth_scale"])
    o3d.io.write_triangle_mesh(f"{out}/meshes/tsdf_bootstrap.ply", mesh0)

    grid, anchor = build_grid_from_mesh(mesh0, cfg["model"]["voxel"], cfg["model"]["band"])
    Q0, b0 = build_prior_laplacian(grid, cfg["model"]["lambda_smooth"],
                                   cfg["model"]["use_anchor"], cfg["model"]["lambda_anchor"], anchor)

    P, Z = depth_points(cfg["data"]["root"], cfg["data"]["stride"], cfg["data"]["max_frames"], cfg["data"]["depth_scale"])
    dd = build_data_diag(grid, P, Z, cfg["model"]["voxel"], cfg["model"]["heteroscedastic"])
    # data term is diagonal: add to Q diagonal
    Q = Q0 + (sp := __import__("scipy.sparse")).sparse.diags(dd, format="csr")
    mu, sinfo = solve_map(Q, b0, cfg["solver"]["tol"], cfg["solver"]["maxiter"])
    var = hutchinson_diag(Q, cfg["variance"]["probes"], cfg["variance"]["tol"], cfg["variance"]["maxiter"])

    Piso, Viso = iso_points(grid, mu, var, nbv_cfg["nbv"].get("eps_band", 0.03))
    pcd = o3d.geometry.PointCloud(o3d.utility.Vector3dVector(Piso))
    if len(Viso):
        c = (Viso - Viso.min())/(Viso.ptp()+1e-9)
        pcd.colors = o3d.utility.Vector3dVector(np.stack([c,0*c,1-c], axis=1))
    o3d.io.write_point_cloud(f"{out}/meshes/iso_points.ply", pcd)

    eye = None; nbv_info = {}
    if nbv_cfg["nbv"].get("enabled", False):
        center = Piso.mean(axis=0) if len(Piso) else np.zeros(3)
        eye, nbv_info = plan_nbv(Piso, Viso, center, nbv_cfg["nbv"]["fov_deg"],
                                 nbv_cfg["nbv"]["candidates"], nbv_cfg["nbv"]["radius_mult"])
        dump_yaml({"next_view_eye": eye.tolist() if eye is not None else None, "info": nbv_info}, f"{out}/metrics/nbv.yaml")

    append_jsonl(f"{out}/logs/run.jsonl", {
        "mode":"ours", "thread_env":thread_env(), "N": int(grid.pts.shape[0]), "solver":sinfo,
        "var_probes": cfg["variance"]["probes"], "nbv": nbv_info
    })

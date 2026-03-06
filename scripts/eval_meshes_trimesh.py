import argparse
import numpy as np
import trimesh
from scipy.spatial import cKDTree

def sample_surface(mesh, n, seed=0):
    # trimesh.sample uses numpy global RNG internally
    np.random.seed(seed)
    return mesh.sample(n)

def nn_dist(a, b):
    tree = cKDTree(b)
    d, _ = tree.query(a, k=1, workers=-1)
    return d

def eval_sets(P, G, thrs_m):
    dp = nn_dist(P, G)   # pred -> gt
    dg = nn_dist(G, P)   # gt -> pred

    out = {}
    out["chamfer_l2_m2"] = float((dp**2).mean() + (dg**2).mean())
    out["acc_mean_m"]    = float(dp.mean())
    out["comp_mean_m"]   = float(dg.mean())

    for thr in thrs_m:
        prec = float((dp < thr).mean())
        rec  = float((dg < thr).mean())
        f = 0.0 if (prec + rec) == 0 else float(2 * prec * rec / (prec + rec))
        out[f"f@{thr*1000:.0f}mm"] = f
        out[f"prec@{thr*1000:.0f}mm"] = prec
        out[f"rec@{thr*1000:.0f}mm"] = rec
    return out

def load_as_points(path, n_samples):
    obj = trimesh.load(path, process=False)

    # If it's a mesh, sample surface; if it's a point cloud, use vertices directly.
    if isinstance(obj, trimesh.Trimesh):
        pts = sample_surface(obj, n_samples, seed=123)
    else:
        # Trimesh PointCloud-like objects usually have .vertices
        pts = np.asarray(obj.vertices)
        if pts.shape[0] > n_samples:
            idx = np.random.default_rng(123).choice(pts.shape[0], size=n_samples, replace=False)
            pts = pts[idx]
    return pts

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--gt", required=True, help="GT mesh .ply")
    ap.add_argument("--pred", required=True, help="Pred mesh or pointcloud .ply")
    ap.add_argument("--n", type=int, default=80000, help="number of samples (for meshes)")
    ap.add_argument("--thr_mm", type=float, nargs="+", default=[10, 20, 50])
    args = ap.parse_args()

    thrs_m = [t / 1000.0 for t in args.thr_mm]

    G = load_as_points(args.gt, args.n)
    P = load_as_points(args.pred, args.n)

    out = eval_sets(P, G, thrs_m)

    print(f"GT:   {args.gt}")
    print(f"PRED: {args.pred}")
    for k in sorted(out.keys()):
        print(f"{k}: {out[k]}")

if __name__ == "__main__":
    main()

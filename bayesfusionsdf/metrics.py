# Purpose: CPU metrics (Chamfer + basic F-score)
from __future__ import annotations
import numpy as np
import open3d as o3d

def _nn_dist(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    pcd = o3d.geometry.PointCloud(o3d.utility.Vector3dVector(b))
    kdt = o3d.geometry.KDTreeFlann(pcd)
    d2 = np.empty((a.shape[0],), dtype=np.float64)
    for i, p in enumerate(a):
        _, idx, dist2 = kdt.search_knn_vector_3d(p, 1)
        d2[i] = dist2[0] if dist2 else 1e9
    return d2

def chamfer_l2(p: np.ndarray, g: np.ndarray) -> float:
    return float(_nn_dist(p, g).mean() + _nn_dist(g, p).mean())

def fscore(p: np.ndarray, g: np.ndarray, thr: float) -> float:
    dp = np.sqrt(_nn_dist(p, g)); dg = np.sqrt(_nn_dist(g, p))
    prec = (dp < thr).mean(); rec = (dg < thr).mean()
    return float(2*prec*rec/(prec+rec+1e-12))

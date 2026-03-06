# Purpose: BayesFusion-SDF core (grid, MAP solve, variance, NBV)
from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
import numpy as np
import scipy.sparse as sp
import scipy.sparse.linalg as spla
import open3d as o3d
import inspect

try:
    from . import bfext  # optional C++ extension
except Exception:
    bfext = None

@dataclass
class Grid:
    pts: np.ndarray          # (N,3) voxel centers
    idx: dict                # (i,j,k)->index
    ijk: np.ndarray          # (N,3) int coords

def build_grid_from_mesh(mesh: o3d.geometry.TriangleMesh, voxel: float, band: float) -> tuple[Grid, np.ndarray]:
    aabb = mesh.get_axis_aligned_bounding_box()
    mn = np.asarray(aabb.min_bound) - band
    mx = np.asarray(aabb.max_bound) + band
    xs = np.arange(mn[0], mx[0]+voxel, voxel)
    ys = np.arange(mn[1], mx[1]+voxel, voxel)
    zs = np.arange(mn[2], mx[2]+voxel, voxel)
    X,Y,Z = np.meshgrid(xs,ys,zs, indexing="ij")
    pts = np.stack([X.ravel(),Y.ravel(),Z.ravel()], axis=1).astype(np.float32)

    tmesh = o3d.t.geometry.TriangleMesh.from_legacy(mesh)
    scene = o3d.t.geometry.RaycastingScene()
    _ = scene.add_triangles(tmesh)
    sd = scene.compute_signed_distance(o3d.core.Tensor(pts)).numpy().astype(np.float32)
    keep = np.abs(sd) <= band
    ptsk = pts[keep]; sdk = sd[keep]
    ijk = np.floor(ptsk/voxel).astype(np.int32)
    idx = {tuple(k): i for i,k in enumerate(ijk)}
    return Grid(ptsk, idx, ijk), sdk

def build_prior_laplacian(grid: Grid, lam_smooth: float, use_anchor: bool, lam_anchor: float, anchor: np.ndarray):
    N = grid.pts.shape[0]
    rows=[]; cols=[]; data=[]
    b = np.zeros((N,), dtype=np.float64)
    nbrs = [(1,0,0),(-1,0,0),(0,1,0),(0,-1,0),(0,0,1),(0,0,-1)]
    for i, c in enumerate(grid.ijk):
        deg = 0
        for d in nbrs:
            nb = (c[0]+d[0], c[1]+d[1], c[2]+d[2])
            j = grid.idx.get(nb, None)
            if j is None:
                continue
            rows.append(i); cols.append(j); data.append(-lam_smooth)
            deg += 1
        rows.append(i); cols.append(i); data.append(lam_smooth*deg + 1e-9)
    if use_anchor:
        rows += list(range(N)); cols += list(range(N)); data += list((lam_anchor*np.ones(N)).tolist())
        b += (lam_anchor*anchor).astype(np.float64)
    Q0 = sp.csr_matrix((np.array(data), (np.array(rows), np.array(cols))), shape=(N,N))
    return Q0, b

def depth_points(root: str, stride: int, max_frames: int, depth_scale: float, pix_stride: int=6, max_pts: int=20000):
    rootp = Path(root)
    w,h = map(int, (rootp/"intrinsic"/"intrinsic.txt").read_text().splitlines()[0].split())
    fx,fy,cx,cy = map(float, (rootp/"intrinsic"/"intrinsic.txt").read_text().splitlines()[1].split())
    depth_files = sorted((rootp/"depth").glob("*.png"))[:max_frames:stride]
    pts=[]
    for df in depth_files:
        i = int(df.stem)
        Twc = np.loadtxt(rootp/"pose"/f"{i:06d}.txt")
        d = np.asarray(o3d.io.read_image(str(df))).astype(np.float32)/depth_scale
        for v in range(0,h,pix_stride):
            y = (v-cy)/fy
            for u in range(0,w,pix_stride):
                z = d[v,u]
                if z<=0:
                    continue
                x = (u-cx)/fx
                pc = np.array([x*z, y*z, z, 1.0], dtype=np.float32)
                pw = (Twc @ pc)[:3]
                pts.append(pw)
                if len(pts) >= max_pts:
                    return np.asarray(pts, dtype=np.float32), np.asarray([z]*len(pts), dtype=np.float32)
    P = np.asarray(pts, dtype=np.float32)
    Z = np.linalg.norm(P, axis=1).astype(np.float32) if len(P) else np.zeros((0,),dtype=np.float32)
    return P, Z

def build_data_diag(grid: Grid, points: np.ndarray, depths: np.ndarray, voxel: float, hetero: bool):
    N = grid.pts.shape[0]
    diag = np.zeros((N,), dtype=np.float64)
    if points.shape[0]==0:
        return diag
    # simple nearest-voxel constraints: phi(v)=0 for voxels hit by depth points
    ijk = np.floor(points/voxel).astype(np.int32)
    a0, b0 = 0.002, 0.0005  # heuristic depth noise
    for pz, c in zip(depths, ijk):
        i = grid.idx.get(tuple(c), None)
        if i is None:
            continue
        sig = (a0 + b0*(pz**2)) if hetero else 0.01
        w = 1.0/(sig*sig)
        diag[i] += w
    return diag

def solve_map(Q: sp.csr_matrix, b: np.ndarray, tol: float, maxiter: int):
    if bfext is not None:
        indptr = Q.indptr.astype(np.int64)
        indices = Q.indices.astype(np.int64)
        data = Q.data.astype(np.float64)
        x, it, res = bfext.cg_solve(indptr, indices, data, b.astype(np.float64), tol, maxiter)
        return x, {"iters": int(it), "resid": float(res), "backend":"bfext"}
    # x, info = spla.cg(Q, b, tol=tol, maxiter=maxiter)
    sig = inspect.signature(spla.cg)
    kwargs = {"maxiter": maxiter}

    # SciPy compatibility: older versions use tol, newer use rtol (+atol)
    if "tol" in sig.parameters:
        kwargs["tol"] = tol
    else:
        kwargs["rtol"] = tol
        if "atol" in sig.parameters:
            kwargs["atol"] = 0.0

    x, info = spla.cg(Q, b, **kwargs)
    return x, info

    return x, {"iters": int(maxiter if info>0 else 0), "resid": float(np.linalg.norm(Q@x-b)), "backend":"scipy"}

def hutchinson_diag(Q: sp.csr_matrix, probes: int, tol: float, maxiter: int, seed: int=0):
    rng = np.random.default_rng(seed)
    N = Q.shape[0]
    acc = np.zeros((N,), dtype=np.float64)
    for _ in range(probes):
        z = rng.choice([-1.0,1.0], size=N).astype(np.float64)
        u, _ = solve_map(Q, z, tol, maxiter)
        acc += z*u
    d = acc / float(probes)
    return np.maximum(d, 1e-12)

def iso_points(grid: Grid, mu: np.ndarray, var: np.ndarray, eps: float):
    m = np.abs(mu) <= eps
    P = grid.pts[m]
    V = var[m]
    return P, V

def plan_nbv(P: np.ndarray, V: np.ndarray, center: np.ndarray, fov_deg: float, candidates: int, radius_mult: float, seed: int=0):
    if P.shape[0]==0:
        return None, {}
    rng = np.random.default_rng(seed)
    fov = np.deg2rad(fov_deg)
    r = radius_mult * np.linalg.norm(P-center, axis=1).max()
    best = (-1e9, None)
    for _ in range(candidates):
        theta = rng.uniform(0, 2*np.pi); phi = rng.uniform(0.2, 1.2)
        eye = center + r*np.array([np.cos(theta)*np.sin(phi), np.sin(theta)*np.sin(phi), np.cos(phi)], dtype=np.float32)
        vdir = (center-eye); vdir = vdir/np.linalg.norm(vdir)
        dirs = P-eye
        dirs = dirs/(np.linalg.norm(dirs, axis=1, keepdims=True)+1e-9)
        vis = (dirs@vdir) > np.cos(fov/2)
        util = float(V[vis].sum())
        if util > best[0]:
            best = (util, eye)
    return best[1], {"utility": best[0]}

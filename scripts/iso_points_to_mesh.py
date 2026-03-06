import argparse
import numpy as np
import open3d as o3d

def clean_mesh(mesh: o3d.geometry.TriangleMesh) -> o3d.geometry.TriangleMesh:
    mesh.remove_degenerate_triangles()
    mesh.remove_duplicated_triangles()
    mesh.remove_duplicated_vertices()
    mesh.remove_non_manifold_edges()
    mesh.compute_vertex_normals()
    return mesh

def try_poisson(pcd: o3d.geometry.PointCloud, depth: int, trim_q: float):
    mesh, dens = o3d.geometry.TriangleMesh.create_from_point_cloud_poisson(pcd, depth=depth)
    if mesh is None:
        return None
    dens = np.asarray(dens)
    if dens.size > 0:
        thr = np.quantile(dens, trim_q)
        mesh = mesh.remove_vertices_by_mask(dens < thr)
    return mesh

def try_bpa(pcd: o3d.geometry.PointCloud, radius_mult=(1.5, 2.5, 3.5)):
    d = np.asarray(pcd.compute_nearest_neighbor_distance(), dtype=np.float64)
    if d.size == 0:
        return None
    avg = float(d.mean())
    radii = [m * avg for m in radius_mult]
    mesh = o3d.geometry.TriangleMesh.create_from_point_cloud_ball_pivoting(
        pcd, o3d.utility.DoubleVector(radii)
    )
    return mesh

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--in_ply", required=True)
    ap.add_argument("--out_ply", required=True)
    ap.add_argument("--voxel_down", type=float, default=0.01, help="Downsample size in meters (0 disables).")
    ap.add_argument("--normal_radius", type=float, default=0.08)
    ap.add_argument("--poisson_depth", type=int, default=8)
    ap.add_argument("--trim_quantile", type=float, default=0.03)
    ap.add_argument("--method", choices=["auto", "poisson", "bpa"], default="auto")
    args = ap.parse_args()

    pcd = o3d.io.read_point_cloud(args.in_ply)
    n0 = len(pcd.points)
    if n0 == 0:
        raise RuntimeError("Empty point cloud.")

    if args.voxel_down and args.voxel_down > 0:
        pcd = pcd.voxel_down_sample(args.voxel_down)

    # Remove obvious outliers (helps meshing stability)
    pcd, _ = pcd.remove_statistical_outlier(nb_neighbors=30, std_ratio=2.0)

    # Normals
    pcd.estimate_normals(
        search_param=o3d.geometry.KDTreeSearchParamHybrid(radius=args.normal_radius, max_nn=30)
    )
    try:
        pcd.orient_normals_consistent_tangent_plane(30)
    except Exception:
        # Some point clouds don't like consistent orientation; continue anyway.
        pass

    n1 = len(pcd.points)
    print(f"points: {n0} -> {n1} (after downsample/outlier removal)")

    mesh = None
    if args.method in ["auto", "poisson"]:
        print("Meshing: Poisson ...")
        mesh = try_poisson(pcd, depth=args.poisson_depth, trim_q=args.trim_quantile)
        if mesh is None:
            print("Poisson returned None.")

    if mesh is None and args.method in ["auto", "bpa"]:
        print("Meshing: Ball Pivoting (BPA) ...")
        mesh = try_bpa(pcd)
        if mesh is None:
            raise RuntimeError("BPA also failed (mesh=None). Try increasing normal_radius or reducing voxel_down.")

    # Crop to pointcloud bbox (keeps it tight)
    bbox = pcd.get_axis_aligned_bounding_box()
    mesh = mesh.crop(bbox)

    mesh = clean_mesh(mesh)
    v = np.asarray(mesh.vertices).shape[0]
    t = np.asarray(mesh.triangles).shape[0]
    if v == 0 or t == 0:
        raise RuntimeError(f"Empty mesh after cleanup (verts={v}, tris={t}). Try different voxel_down/normal_radius.")

    ok = o3d.io.write_triangle_mesh(args.out_ply, mesh)
    print("Wrote:", args.out_ply, "ok=", ok)
    print("verts=", v, "tris=", t)

if __name__ == "__main__":
    main()

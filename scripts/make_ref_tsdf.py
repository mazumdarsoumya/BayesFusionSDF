import argparse
from pathlib import Path
import numpy as np
import open3d as o3d

def read_intrinsics(path: Path):
    lines = path.read_text().splitlines()
    w, h = map(int, lines[0].split())
    fx, fy, cx, cy = map(float, lines[1].split())
    K = o3d.camera.PinholeCameraIntrinsic(w, h, fx, fy, cx, cy)
    return K, w, h

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data_root", required=True)
    ap.add_argument("--depth_scale", type=float, default=10000.0)
    ap.add_argument("--voxel", type=float, default=0.02)
    ap.add_argument("--trunc", type=float, default=0.06)
    ap.add_argument("--stride", type=int, default=1)
    ap.add_argument("--max_frames", type=int, default=999999)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    root = Path(args.data_root)
    K, w, h = read_intrinsics(root/"intrinsic"/"intrinsic.txt")

    vol = o3d.pipelines.integration.ScalableTSDFVolume(
        voxel_length=args.voxel,
        sdf_trunc=args.trunc,
        color_type=o3d.pipelines.integration.TSDFVolumeColorType.NoColor
    )

    depth_files = sorted((root/"depth").glob("*.png"))[:args.max_frames:args.stride]
    zero_color = o3d.geometry.Image(np.zeros((h, w, 3), dtype=np.uint8))

    for df in depth_files:
        i = int(df.stem)
        Twc = np.loadtxt(root/"pose"/f"{i:06d}.txt")
        rgbd = o3d.geometry.RGBDImage.create_from_color_and_depth(
            zero_color,
            o3d.io.read_image(str(df)),
            depth_scale=args.depth_scale,
            depth_trunc=10.0,
            convert_rgb_to_intensity=False
        )
        vol.integrate(rgbd, K, np.linalg.inv(Twc))

    mesh = vol.extract_triangle_mesh()
    mesh.compute_vertex_normals()

    outp = Path(args.out)
    outp.parent.mkdir(parents=True, exist_ok=True)
    ok = o3d.io.write_triangle_mesh(str(outp), mesh)
    print("Wrote:", outp, "ok=", ok)
    print("verts=", np.asarray(mesh.vertices).shape[0], "tris=", np.asarray(mesh.triangles).shape[0])

if __name__ == "__main__":
    main()

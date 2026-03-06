# Purpose: CPU TSDF baseline using Open3D TSDFVolume
from __future__ import annotations
from pathlib import Path
import numpy as np
import open3d as o3d

def _read_intrinsics(path: Path):
    w,h = map(int, path.read_text().splitlines()[0].split())
    fx,fy,cx,cy = map(float, path.read_text().splitlines()[1].split())
    K = o3d.camera.PinholeCameraIntrinsic(w, h, fx, fy, cx, cy)
    return K, (w,h), fx,fy,cx,cy

def integrate_tsdf(root: str, stride: int, max_frames: int, voxel: float, trunc: float, depth_scale: float):
    rootp = Path(root)
    K, (w,h), *_ = _read_intrinsics(rootp/"intrinsic"/"intrinsic.txt")
    vol = o3d.pipelines.integration.ScalableTSDFVolume(
        voxel_length=voxel, sdf_trunc=trunc,
        color_type=o3d.pipelines.integration.TSDFVolumeColorType.NoColor
    )
    depth_files = sorted((rootp/"depth").glob("*.png"))[:max_frames:stride]
    zero_color = o3d.geometry.Image((np.zeros((h,w,3))).astype(np.uint8))
    for df in depth_files:
        i = int(df.stem)
        Twc = np.loadtxt(rootp/"pose"/f"{i:06d}.txt")
        rgbd = o3d.geometry.RGBDImage.create_from_color_and_depth(
            zero_color, o3d.io.read_image(str(df)),
            depth_scale=depth_scale, depth_trunc=10.0, convert_rgb_to_intensity=False
        )
        vol.integrate(rgbd, K, np.linalg.inv(Twc))
    mesh = vol.extract_triangle_mesh()
    mesh.compute_vertex_normals()
    return mesh

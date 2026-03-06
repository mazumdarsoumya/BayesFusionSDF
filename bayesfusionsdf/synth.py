# Purpose: Synthetic depth/pose generator (sphere) for smoke tests
from __future__ import annotations
from pathlib import Path
import numpy as np
import open3d as o3d

def _look_at(eye, center=(0,0,0), up=(0,0,1)):
    """Create a camera-to-world pose Twc for a pinhole camera.

    Convention:
      - camera +Z points forward
      - camera +X points right
      - camera +Y points down (image v increases downward)

    This makes synthetic depth generation consistent with Open3D's pinhole model.
    """
    import numpy as np

    eye = np.asarray(eye, dtype=np.float64)
    center = np.asarray(center, dtype=np.float64)
    up = np.asarray(up, dtype=np.float64)

    z = center - eye
    nz = np.linalg.norm(z)
    if nz < 1e-9:
        raise ValueError("eye and center are the same point")
    z = z / nz  # forward (+Z) in world coords

    # If forward is parallel to up, choose a different up to avoid degeneracy
    if abs(np.dot(z, up) / (np.linalg.norm(up) + 1e-12)) > 0.99:
        up = np.array([0.0, 1.0, 0.0], dtype=np.float64)

    x = np.cross(z, up)
    nx = np.linalg.norm(x)
    if nx < 1e-9:
        raise ValueError("degenerate look_at: cross(z, up) is near zero")
    x = x / nx  # right (+X)

    y = np.cross(z, x)  # ensures right-handed frame: x × y = z

    T = np.eye(4, dtype=np.float64)
    T[:3, :3] = np.stack([x, y, z], axis=1)
    T[:3, 3] = eye
    return T


def make_sphere_scene(out_dir: str, n_frames=12, w=64, h=64, f=70.0, radius=0.6, depth_scale=1000.0):
    out = Path(out_dir); (out/"depth").mkdir(parents=True, exist_ok=True)
    (out/"pose").mkdir(exist_ok=True); (out/"intrinsic").mkdir(exist_ok=True); (out/"gt").mkdir(exist_ok=True)
    fx=fy=f; cx=(w-1)/2; cy=(h-1)/2
    with open(out/"intrinsic"/"intrinsic.txt","w",encoding="utf-8") as f0:
        f0.write(f"{w} {h}\n{fx} {fy} {cx} {cy}\n")
    mesh = o3d.geometry.TriangleMesh.create_sphere(radius=radius)
    mesh.compute_vertex_normals()
    o3d.io.write_triangle_mesh(str(out/"gt"/"gt_mesh.ply"), mesh)
    for i in range(n_frames):
        ang = 2*np.pi*i/n_frames
        eye = (1.5*np.cos(ang), 1.5*np.sin(ang), 0.6)
        Twc = _look_at(eye)
        np.savetxt(out/"pose"/f"{i:06d}.txt", Twc)
        depth = np.zeros((h,w), dtype=np.float32)
        for v in range(h):
            y = (v-cy)/fy
            for u in range(w):
                x = (u-cx)/fx
                ray_c = np.array([x,y,1.0]); ray_c/=np.linalg.norm(ray_c)
                R = Twc[:3,:3]; t = Twc[:3,3]
                ray_w = R@ray_c; o = t
                b = 2*np.dot(o, ray_w); c = np.dot(o,o)-radius*radius
                disc = b*b-4*c
                if disc>0:
                    t0 = (-b-np.sqrt(disc))/2.0
                    if t0>0: depth[v,u]=t0
        im = (depth*depth_scale).astype(np.uint16)
        o3d.io.write_image(str(out/"depth"/f"{i:06d}.png"), o3d.geometry.Image(im))

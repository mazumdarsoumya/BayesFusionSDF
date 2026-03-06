# Purpose: Build optional C++ pybind11 extension (Eigen + OpenMP CG)
from setuptools import setup
from pybind11.setup_helpers import Pybind11Extension, build_ext

ext_modules = [
    Pybind11Extension(
        "bayesfusion_sdf.bfext",
        ["cpp/bfext.cpp"],
        cxx_std=17,
        extra_compile_args=["-O3"],
    )
]

setup(
    name="bayesfusion-sdf",
    package_dir={"": "src"},
    packages=["bayesfusion_sdf"],
    ext_modules=ext_modules,
    cmdclass={"build_ext": build_ext},
)

"""Setup file for depth-quality python package."""

import glob
from setuptools import setup

if __name__ == '__main__':
    setup(
        name="depthquality",
        version="0.0.1",
        packages=['depthquality'],
        package_dir={'': 'src'},
        package_data={'depthquality': glob.glob('meshes/*.obj')},
        author="Root AI",
        author_email="mprat@root-ai.com",
        description="Analyzing depth camera quality with 3D printed fixtures.",
        license="",
        python_requires='>=3.5',
        install_requires=[
            "numpy>=1.16",
            "open3d-python>=0.14.1",
            # we take a dependency on opencv-contrib-python because the
            # library for detecting ArUco markers is here
            "opencv-contrib-python>=3.0,<4.0"
        ]
    )

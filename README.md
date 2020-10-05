# Measuring Depth Quality With 3D-Printed Fixtures

![Pointcloud-Mesh Alignment](https://user-images.githubusercontent.com/829379/55204675-4e349280-51a6-11e9-9eb6-824417855674.png)

## Overview

This repository provides models and code to do depth quality assessment of off-the-shelf cameras using 3D printed fixtures.

This accompanies a workshop paper currently under review for the ICRA 2019 HAMM workshop.

## Dependencies

* [PyMesh](https://github.com/PyMesh/PyMesh) should be compiled and installed separately according to the instructions given in PyMesh. We don't take a dependency in this package because of high installation / compilation time of its various dependencies.

The barebones dependencies (except PyMesh) are included in this project's `setup.py` file. If you want to develop, run tests, or run visualizations, it is recommended that you run `pip install -r requirements-dev.txt` to install the development dependencies.

## Fixture Fabrication

To produce the test fixtures, you need to:

1) Lasercut the back plate. The PDF is provided in `fabrication/backplate.pdf`; the black lines should be cut, and the red lines should be etched. The settings will depend on the lasercutter you use.
2) Print and affix the ArUco fiducials into the etched portion of the backplate. The fiducials (to scale) are provided in the `fabrication/fiducials/` folder as SVGs of 20 mm by 20 mm.
3) 3D print the meshes. The meshes are located in `fabrication/3dprinting/` as STL files, and can be directly imported into 3D printing software. Any modifications can be made directly to the meshes, as long as a resulting STL / OBJ is produced as a reference mesh. The settings you need to use on your 3D printer will vary, but it is recommended to have a dual-filament printer capable of printing support material to accurately make these prints.

## Installation

It is recommended to use a Python virtual environment to run this code, to not interfere with other dependencies. `PyMesh` must be installed in the virtual environment before installing the rest of the package.

Install the package with `python setup.py develop`; the data sources (i.e. the meshes) are not available when running `python setup.py install`, so don't do that!

### Typical Usage

After fabricating the desired fixture, set up your test environment and capture some images and data using your camera's API. You will also need to know the depth scale at which the depth values are calculated. This will vary per-camera, and therefore you will have to do some work to get these files:

1) An RGB or grayscale image - for doing ArUco detection. It can be saved in any format that can be read by `opencv` - a PNG is recommended.
2) Using your camera's API, deproject the depth image to compute the pointcloud. Save this pointcloud in a standard pointcloud format like PLY. Anything that can be read by [`open3d.read_point_cloud`](http://www.open3d.org/docs/python_api/io.html#open3d.io.read_point_cloud) should work.
3) The camera intrinsics of the sensor in (`.json`) format. See this [example](src/tests/data/angled_plates/camera_matrix.json) for the formatting.

If you are using one of the reference meshes provided directly with this repository, simply import it directly from the repo:

```
from depthquality.meshes import VERTICAL_CYLINDERS
```

And using the three files you saved (`.png`, `.json`, `.ply`) you can run the evaluation pipeline:


```
import depthquality.quality as quality

# this will align the pointcloud to the provided reference mesh
# and estimate the camera angle at which the image was captured
aligned_pointcloud, camera_angle = quality.align_pointcloud_to_reference(
    reference_mesh=VERTICAL_CYLINDERS,
    rgb_filename="img.png",
    camera_matrix_filename="camera_matrix.json",
    pointcloud_filename="sparse_world.ply",
    depth_scale=0.001)

# this will crop the pointcloud to the relevant working area
cropped_pointcloud = quality.clip_pointcloud_to_pattern_area(
    reference_mesh=VERTICAL_CYLINDERS,
    aligned_pointcloud, depth_scale=0.001)

# this will actually compute the RMSE and density of the mesh
rmse, density = quality.calculate_rmse_and_density(
    ground_truth_mesh=VERTICAL_CYLINDERS,
    cropped_pointcloud=cropped_pointcloud,
    depth_scale=0.001,
    camera_angle=camera_angle)
```

See the example `jupyter notebook` in `notebooks/alignment.ipynb` for some example data and a visualization.

### Extending to Custom Reference Meshes

You can produce custom reference meshes (and 3D print them accordingly). Produce an OBJ file of the fixture you want to print and create a reference mesh to use:

```
from depthquality.meshes import ReferenceMesh
reference_mesh = ReferenceMesh(path='/path/to/your/file.obj')
```

And use the same pipeline as above.

## License and Citation

This projected is released under the MIT License - see the LICENSE file for details.

If you found this work useful, please cite it, and reach out to us though a Github issue! We'd love to hear about what you're using this for.

```
@misc{1903.09169,
Author = {Michele Pratusevich and Jason Chrisos and Shreyas Aditya},
Title = {Quantitative Depth Quality Assessment of RGBD Cameras At Close Range Using 3D Printed Fixtures},
Year = {2019},
Eprint = {arXiv:1903.09169},
}
```

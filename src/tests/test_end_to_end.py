"""End to end API test."""
import os
import pytest
import depthquality.quality as quality
import depthquality.meshes as meshes


def get_test_files(subfolder):
    return {
        "rgb": os.path.join(os.path.dirname(__file__), "data/{}/1.png".format(subfolder)),
        "camera_matrix": os.path.join(os.path.dirname(__file__), "data/{}/camera_matrix.json".format(subfolder)),
        "pointcloud": os.path.join(os.path.dirname(__file__), "data/{}/1.ply".format(subfolder)),
        "depth_scale": 0.001
    }


def delete_all_keep_original(subfolder, original_files):
    # delete any files that were added as a result of the tests
    for file in os.listdir(os.path.join(os.path.dirname(__file__), "data/{}".format(subfolder))):
        full_filename = os.path.join(os.path.dirname(__file__), "data", subfolder, file)
        if full_filename not in (original_files["rgb"], original_files["camera_matrix"],
                                 original_files["pointcloud"]):
            os.remove(full_filename)


@pytest.fixture(scope="module")
def vert_cylinders():
    """Known sample from collecting a cylinder to use as a test fixture."""
    files = get_test_files("vert_cylinders")
    yield files

    delete_all_keep_original("vert_cylinders", files)


@pytest.fixture(scope="module")
def horiz_cylinders():
    """Known sample from collecting a cylinder to use as a test fixture."""
    files = get_test_files("horiz_cylinders")
    yield files

    delete_all_keep_original("horiz_cylinders", files)


@pytest.fixture(scope="module")
def spheres():
    """Known sample from collecting a cylinder to use as a test fixture."""
    files = get_test_files("spheres")
    yield files

    delete_all_keep_original("spheres", files)


@pytest.fixture(scope="module")
def angled_plates():
    """Known sample from collecting a cylinder to use as a test fixture."""
    files = get_test_files("angled_plates")
    yield files

    delete_all_keep_original("angled_plates", files)


def run_alignment_calculation_test(
        reference_fixture, pytest_fixture, expected_rmse, expected_density):
    """Test runner for running pipeline with the fixtures."""
    aligned_pointcloud, camera_angle = quality.align_pointcloud_to_reference(
        reference_fixture,
        pytest_fixture["rgb"],
        pytest_fixture["camera_matrix"],
        pytest_fixture["pointcloud"], depth_scale=pytest_fixture["depth_scale"])

    cropped_pointcloud = quality.clip_pointcloud_to_pattern_area(
        reference_fixture, aligned_pointcloud, depth_scale=pytest_fixture["depth_scale"])

    rmse, density = quality.calculate_rmse_and_density(
        ground_truth_mesh=reference_fixture,
        cropped_pointcloud=cropped_pointcloud,
        depth_scale=pytest_fixture["depth_scale"],
        camera_angle=camera_angle)

    assert pytest.approx(rmse, 0.01) == expected_rmse
    assert pytest.approx(density, 0.01) == expected_density


def test_vertical_cylinder(vert_cylinders):
    """Test end-to-end with known result from vertical cylinders and PLY."""
    run_alignment_calculation_test(
        reference_fixture=meshes.VERTICAL_CYLINDERS,
        pytest_fixture=vert_cylinders,
        expected_rmse=1.676,
        expected_density=1.765)


def test_horiz_cylinder(horiz_cylinders):
    """Test end-to-end with known result from vertical cylinders and PLY."""
    run_alignment_calculation_test(
        reference_fixture=meshes.HORIZONTAL_CYLINDERS,
        pytest_fixture=horiz_cylinders,
        expected_rmse=3.358,
        expected_density=0.714)


def test_spheres(spheres):
    """Test end-to-end with known result from vertical cylinders and PLY."""
    run_alignment_calculation_test(
        reference_fixture=meshes.SPHERES,
        pytest_fixture=spheres,
        expected_rmse=2.811,
        expected_density=1.239)


def test_angled_plates(angled_plates):
    """Test end-to-end with known result from vertical cylinders and PLY."""
    run_alignment_calculation_test(
        reference_fixture=meshes.ANGLED_PLATES,
        pytest_fixture=angled_plates,
        expected_rmse=2.233,
        expected_density=1.779)

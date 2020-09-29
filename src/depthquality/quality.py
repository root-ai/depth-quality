"""All functions related to generating quality metrics."""
import os
import numpy as np
import open3d
import pymesh
import cv2
import json
from depthquality import transformations as tfms
from depthquality.fiducials import detect_arucos


def align_pointcloud_to_reference(
        reference_mesh, rgb_filename, camera_matrix_filename, pointcloud_filename, depth_scale):
    img = cv2.imread(rgb_filename)
    detected_arucos = detect_arucos(img)

    with open(camera_matrix_filename, 'r') as j_file:
        camera_matrix = json.load(j_file)

    # the PLY files saved from librealsense are JUST vertices (no faces)
    # so they are pretty easy to manipulate
    pointcloud = open3d.read_point_cloud(pointcloud_filename)

    # Create a dictionary of the aruco corner points so as to find the 3D coordinates when
    # deprojecting the pointcloud.
    corner_coordinates = {}
    for aruco_id, corners in detected_arucos.items():
        for location, corner in corners.items():
            corner_coordinates[(int(corner[1]), int(corner[0]))] = []

    compute_corner_coordinates(pointcloud, camera_matrix, corner_coordinates)
    # go through the detected arucos to get the reference coordinates, and concatenate
    # two lists of matrices corresponding to both
    measured_coords = []
    reference_coords = []
    for aruco_id, corners in detected_arucos.items():
        for location, corner in corners.items():
            # match the detected corner to the appropriate corner
            # in the reference mesh
            reference_coordinate = reference_mesh.get_fiducial_coordinate(
                fiducial_id=aruco_id, location=location)
            detected_coordinate = corner_coordinates[(int(corner[1]), int(corner[0]))]

            # if the depth is a valid value, then we can use it for estimation
            if len(detected_coordinate) != 0:
                measured_coords.append(detected_coordinate)
                reference_coords.append(reference_coordinate)

    # convert the coordinates into arrays for processing, and make sure the reference
    # is scaled by the depth_scale of the detected pointcloud
    measured_coords = np.array(measured_coords)
    reference_coords = np.array(reference_coords) * depth_scale

    # estimate the rigid transform
    rigid_transform = tfms.affine_matrix_from_points(
        measured_coords.T, reference_coords.T, shear=False, scale=False)

    # estimate the camera_angle by multiplying the "ideal camera angle"
    # by the inverse of the rotation matrix
    camera_angle = rigid_transform[:3,:3] @ np.array([0, 0, -1])
    # transform the pointcloud
    # and write a new one
    pointcloud.transform(rigid_transform)
    return pointcloud, camera_angle


def clip_pointcloud_to_pattern_area(reference_mesh, aligned_pointcloud, depth_scale):
    # clip the pointcloud to the area of interest
    # we only want to clip INSIDE the area inside the pattern plate
    # TODO: get these numbers from the reference_mesh.pattern_plate mesh
    working_height = 82.55
    working_width = working_height

    # calculate the min and max z for clipping based on the pattern meshes
    # specific to each reference mesh
    min_model_z = np.min([[s.bbox[0][2], s.bbox[1][2]] for s in reference_mesh.pattern_meshes])
    max_model_z = np.max([[s.bbox[0][2], s.bbox[1][2]] for s in reference_mesh.pattern_meshes])

    # buffer that we consider our "error bound" in Z
    buffer_bounds = 3  # mm

    # we know the reference mesh is zero-centered, so take the bounds centered at the origin
    # as well
    min_bound = np.array([-working_width / 2, -working_height / 2, min_model_z - buffer_bounds])
    max_bound = np.array([working_width / 2, working_height / 2, max_model_z + buffer_bounds])

    cropped_pointcloud = open3d.geometry.crop_point_cloud(
        aligned_pointcloud,
        min_bound=depth_scale * min_bound,
        max_bound=depth_scale * max_bound)

    return cropped_pointcloud

def compute_corner_coordinates(pointcloud, camera_matrix, corner_coordinates):

    for point in np.asarray(pointcloud.points):
        u = np.floor(camera_matrix["fx"] * point[0] / point[2] + camera_matrix["ppx"])
        v = np.floor(camera_matrix["fy"] * point[1] / point[2] + camera_matrix["ppy"])

        if (v, u) in corner_coordinates.keys():
            corner_coordinates[(v,u)] = point


def calculate_rmse_and_density(ground_truth_mesh, cropped_pointcloud, depth_scale, camera_angle):
    # need to get the reference mesh and the pointcloud in the same units
    squared_distances, _, _ = pymesh.distance_to_mesh(
        ground_truth_mesh.reference_mesh, np.asarray(cropped_pointcloud.points) / depth_scale)

    rmse = np.sqrt(np.sum(squared_distances) / len(squared_distances))
    distance_thresh = 2  # mm of distance
    threshold = distance_thresh ** 2
    num_valid_pixels = len(squared_distances[squared_distances < threshold])

    valid_pattern_surface_area = ground_truth_mesh.get_pattern_surface_area(
        camera_angle=camera_angle)

    return rmse, num_valid_pixels / valid_pattern_surface_area


def save_pointcloud(original_filename, new_suffix, pointcloud):
    basepath, ext = os.path.splitext(original_filename)
    transformed_pointcloud_filename = basepath + "_" + new_suffix + ext
    open3d.write_point_cloud(transformed_pointcloud_filename, pointcloud)

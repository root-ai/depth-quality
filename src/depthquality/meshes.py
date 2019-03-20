"""All functionality related to the ground-truth meshes."""
import pymesh
import pkg_resources
import numpy as np
from depthquality.fiducials import TOP_LEFT, TOP_RIGHT, BOTTOM_LEFT, BOTTOM_RIGHT


class ReferenceMesh:
    def __init__(self, path, backplate_thickness=6.35):
        self.path = path
        self.reference_mesh = pymesh.load_mesh(path)

        # we want to separate the submeshes based on face connectivity,
        # since that will give us all the discrete parts
        self.submeshes = pymesh.separate_mesh(
            self.reference_mesh, connectivity_type="face")

        # get all the pattern meshes, which are the submeshes that are
        # NOT the: backplate, pattern plate, or fiducial tag locations
        self.backplate_thickness = backplate_thickness
        self.pattern_plate_thickness = 3
        self.pattern_meshes = []
        self.fiducial_meshes = []
        self.backplate_mesh = None
        self.pattern_plate_mesh = None

        for submesh in self.submeshes:
            if not submesh.is_closed():
                # these are the fiducial marker locations
                # because they are the ones that are 1-dimensional
                self.fiducial_meshes.append(submesh)
            elif (submesh.bbox[0][2] == 0 and
                  submesh.bbox[1][2] == self.backplate_thickness) or \
                    (submesh.bbox[1][2] == 0 and
                     submesh.bbox[0][2] == self.backplate_thickness):
                # this is the backplate, since the bounding box extends to 0
                self.backplate_mesh = submesh
            elif (submesh.bbox[0][2] ==
                  self.backplate_thickness + self.pattern_plate_thickness and
                  submesh.bbox[1][2] == self.backplate_thickness) or \
                    (submesh.bbox[1][2] ==
                     self.backplate_thickness + self.pattern_plate_thickness and
                     submesh.bbox[0][2] == self.backplate_thickness):
                # this is the pattern plate, since the bounding box starts
                # from the end of the backplate and goes the thickness of
                # the pattern plate
                self.pattern_plate_mesh = submesh
            else:
                self.pattern_meshes.append(submesh)

        # the fiducial locations on the reference mesh
        # TODO: generate these automatically from the meshes
        self.fiducial_locations = {
            # top left
            231: {
                TOP_LEFT: [-75.5625, 48.575, self.backplate_thickness],
                TOP_RIGHT: [-55.5625, 48.575, self.backplate_thickness],
                BOTTOM_RIGHT: [-55.5625, 28.575, self.backplate_thickness],
                BOTTOM_LEFT: [-75.5625, 28.575, self.backplate_thickness],
            },
            # top right
            123: {
                TOP_LEFT: [55.5625, 48.575, self.backplate_thickness],
                TOP_RIGHT: [75.5625, 48.575, self.backplate_thickness],
                BOTTOM_RIGHT: [75.5625, 28.575, self.backplate_thickness],
                BOTTOM_LEFT: [55.5625, 28.575, self.backplate_thickness],
            },
            # bottom left
            114: {
                TOP_LEFT: [-75.5625, -28.575, self.backplate_thickness],
                TOP_RIGHT: [-55.5625, -28.575, self.backplate_thickness],
                BOTTOM_RIGHT: [-55.5625, -48.575, self.backplate_thickness],
                BOTTOM_LEFT: [-75.5625, -48.575, self.backplate_thickness],
            },
            # bottom right
            141: {
                TOP_LEFT: [55.5625, -28.575, self.backplate_thickness],
                TOP_RIGHT: [75.5625, -28.575, self.backplate_thickness],
                BOTTOM_RIGHT: [75.5625, -48.575, self.backplate_thickness],
                BOTTOM_LEFT: [55.5625, -48.575, self.backplate_thickness],
            }
        }

    def get_pattern_surface_area(self, camera_angle=np.array([0, 0, 1])):
        total_surface_area = 0
        for pattern_mesh in self.pattern_meshes:
            # add the face normal and face area attributes
            pattern_mesh.add_attribute("face_normal")
            pattern_mesh.add_attribute("face_area")

            # the face normals are all unit normals
            face_normals = pattern_mesh.get_face_attribute("face_normal")
            face_area = pattern_mesh.get_face_attribute("face_area")

            faces_within_angle_of_pos_z = np.arccos(np.dot(face_normals, camera_angle)) < np.pi / 2
            visible_surface_area = np.sum(face_area[faces_within_angle_of_pos_z])
            total_surface_area += visible_surface_area
        return total_surface_area

    def get_fiducial_coordinate(self, fiducial_id, location):
        """Return a 3D XYZ coordinate from the reference mesh based on fiducial_id and location."""
        return self.fiducial_locations[fiducial_id][location]


VERTICAL_CYLINDERS = ReferenceMesh(
    path=pkg_resources.resource_filename('depthquality', '../meshes/vertical_cylinders.obj'))
HORIZONTAL_CYLINDERS = ReferenceMesh(
    path=pkg_resources.resource_filename('depthquality', '../meshes/horizontal_cylinders.obj'))
SPHERES = ReferenceMesh(
    path=pkg_resources.resource_filename('depthquality', '../meshes/spheres.obj'))
ANGLED_PLATES = ReferenceMesh(
    path=pkg_resources.resource_filename('depthquality', '../meshes/angled_plates.obj'))

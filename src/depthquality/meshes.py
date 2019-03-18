"""All functionality related to the ground-truth meshes."""
import pymesh
import pkg_resources


class ReferenceMesh:
    def __init__(self, path, backplate_thickness=6.35):
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

        # TODO: robustify
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


VERTICAL_CYLINDERS = ReferenceMesh(
    path=pkg_resources.resource_filename('depthquality', 'meshes/vertical_cylinders.obj'))
HORIZONTAL_CYLINDERS = ReferenceMesh(
    path=pkg_resources.resource_filename('depthquality', 'meshes/horizontal_cylinders.obj'))
SPHERES = ReferenceMesh(
    path=pkg_resources.resource_filename('depthquality', 'meshes/spheres.obj'))
ANGLED_PLATES = ReferenceMesh(
    path=pkg_resources.resource_filename('depthquality', 'meshes/angled_plates.obj'))

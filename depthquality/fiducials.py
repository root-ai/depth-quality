"""Everything related to the fiducials used for alignment."""

from collections import namedtuple

Location = namedtuple("Location", ("location", ))

TOP_LEFT = Location("top_left")
TOP_RIGHT = Location("top_right")
BOTTOM_LEFT = Location("bottom_left")
BOTTOM_RIGHT = Location("bottom_right")


class Fiducial:
    def __init__(
            self, fiducial_id, top_left_coord, top_right_coord,
            bottom_left_coord, bottom_right_coord):
        self.fiducial_id = fiducial_id
        self.coordinates = {
            TOP_LEFT: top_left_coord,
            TOP_RIGHT: top_right_coord,
            BOTTOM_LEFT: bottom_left_coord,
            BOTTOM_RIGHT: bottom_right_coord
        }


# TODO: generate these automatically from the meshes
BACKPLATE_THICKNESS = 6.35
TOP_LEFT_FIDUCIAL = Fiducial(
    fiducial_id=231,
    top_left_coord=[-55.5625, 28.575, BACKPLATE_THICKNESS],
    top_right_coord=[-75.5625, 28.575, BACKPLATE_THICKNESS],
    bottom_left_coord=[-55.5625, 48.575, BACKPLATE_THICKNESS],
    bottom_right_coord=[-75.5625, 48.575, BACKPLATE_THICKNESS]
)
TOP_RIGHT_FIDUCIAL = Fiducial(
    fiducial_id=123,
    top_left_coord=[55.5625, 28.575, BACKPLATE_THICKNESS],
    top_right_coord=[75.5625, 28.575, BACKPLATE_THICKNESS],
    bottom_left_coord=[55.5625, 48.575, BACKPLATE_THICKNESS],
    bottom_right_coord=[75.5625, 48.575, BACKPLATE_THICKNESS]
)
BOTTOM_LEFT_FIDUCIAL = Fiducial(
    fiducial_id=114,
    top_left_coord=[-55.5625, -28.575, BACKPLATE_THICKNESS],
    top_right_coord=[-75.5625, -28.575, BACKPLATE_THICKNESS],
    bottom_left_coord=[-55.5625, -48.575, BACKPLATE_THICKNESS],
    bottom_right_coord=[-75.5625, -48.575, BACKPLATE_THICKNESS]
)
BOTTOM_RIGHT_FIDUCIAL = Fiducial(
    fiducial_id=141,
    top_left_coord=[55.5625, -28.575, BACKPLATE_THICKNESS],
    top_right_coord=[75.5625, -28.575, BACKPLATE_THICKNESS],
    bottom_left_coord=[55.5625, -48.575, BACKPLATE_THICKNESS],
    bottom_right_coord=[75.5625, -48.575, BACKPLATE_THICKNESS]
)

"""Everything related to the fiducials used for alignment."""

from collections import namedtuple
import cv2

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


def detect_arucos(img):
    # detect the aruco tags
    aruco_dict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_1000)
    params = cv2.aruco.DetectorParameters_create()
    params.perspectiveRemovePixelPerCell = 10
    params.perspectiveRemoveIgnoredMarginPerCell = 0.1
    params.cornerRefinementMethod = cv2.aruco.CORNER_REFINE_CONTOUR
    marker_corners, marker_ids, _ = cv2.aruco.detectMarkers(
        img, aruco_dict, parameters=params)

    detected_arucos = {}
    for corners, aruco_id in zip(marker_corners, marker_ids):
        # corners is always in top-left, top-right, bottom-right, bottom-left order
        detected_arucos[aruco_id[0]] = {
            TOP_LEFT: corners[0][0],
            TOP_RIGHT: corners[0][1],
            BOTTOM_RIGHT: corners[0][2],
            BOTTOM_LEFT: corners[0][3]
        }
    return detected_arucos

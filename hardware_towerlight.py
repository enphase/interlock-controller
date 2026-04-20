import cadquery as cq
from typing import List, Tuple
from hardware_metric_nut import MetricNut, apply_hex_nut_tool, M4_NUT

HOLE_PATTERN_L = 36.0
HOLE_PATTERN_W = 36.0


def apply_tower_light_cutouts(
    wp: cq.Workplane,
    location: Tuple[float, float],
    depth: float,
    *,
    tol: float = 0.2,
) -> cq.Workplane:
    """
    Applies the hole for the tower light wiring and mounting holes
    """
    res = wp

    # Mounting hole pattern
    res = apply_hex_nut_tool(
        res,
        [
            (location[0] - HOLE_PATTERN_L / 2, location[1] - HOLE_PATTERN_W / 2),
            (location[0] - HOLE_PATTERN_L / 2, location[1] + HOLE_PATTERN_W / 2),
            (location[0] + HOLE_PATTERN_L / 2, location[1] - HOLE_PATTERN_W / 2),
            (location[0] + HOLE_PATTERN_L / 2, location[1] + HOLE_PATTERN_W / 2),
        ],
        M4_NUT,
        depth=depth,
        chamfer=0.5,
        tol_clearance=tol,
    )

    # wiring hole
    res = (
        res.copyWorkplane(wp)
        .pushPoints([location])
        .circle(5.0 + tol * 2)
        .cutBlind("next")
    )

    return res

import cadquery as cq
from typing import List, Tuple
from .fasteners import MetricNut, cut_hex_nut_pocket

PANEL_CUTOUT_WIDTH = 27.3
PANEL_CUTOUT_HEIGHT = 31.4
PANEL_CUTOUT_RADIUS = 1.0
HOLE_SPACING = 36.0


def cut_719w_power_entry(
    wp: cq.Workplane,
    locations: List[Tuple[float, float]],
    nut: MetricNut,
    depth: float,
    *,
    tol: float = 0.2,
    chamfer: float = 0.0,
) -> cq.Workplane:
    """
    Cuts the panel cutout for the 719W-00/02 AC power entry module.
    """
    sketch = (
        cq.Sketch()
        .rect(PANEL_CUTOUT_WIDTH + tol * 2, PANEL_CUTOUT_HEIGHT + tol * 2)
        .vertices()
        .fillet(PANEL_CUTOUT_RADIUS)
    )

    res = wp

    # Main rectangular cutout
    res = (
        res.copyWorkplane(cq.Workplane(wp.plane))
        .pushPoints(locations)
        .placeSketch(sketch)
        .cutThruAll()
    )

    # Calculate hex nut locations relative to each location
    nut_locations = []
    for loc in locations:
        cx, cy = loc
        nut_locations.extend(
            [
                (cx - HOLE_SPACING / 2, cy),
                (cx + HOLE_SPACING / 2, cy),
            ]
        )

    # Apply hex nut cutouts
    res = cut_hex_nut_pocket(
        res.copyWorkplane(cq.Workplane(wp.plane)),
        nut_locations,
        nut,
        depth=depth,
        chamfer=chamfer,
        angle=30.0,
    )

    return res

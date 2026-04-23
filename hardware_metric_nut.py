import math

import cadquery as cq
from typing import NamedTuple, List, Tuple


class MetricNut(NamedTuple):
    """Nominal dimensions for standard metric hex nuts."""

    thread_size: str
    across_flats: float
    thickness: float
    clearance_dia: float

    def diameter(self) -> float:
        """Returns the circumscribed diameter (distance across corners)."""
        return self.across_flats / (math.sqrt(3) / 2)


# Nominal dimensions from ISO/DIN standards for M3 hex nuts
M3_NUT = MetricNut(thread_size="M3", across_flats=5.5, thickness=2.4, clearance_dia=3.2)
M4_NUT = MetricNut(thread_size="M4", across_flats=7.0, thickness=3.2, clearance_dia=4.3)


def apply_hex_nut_tool(
    wp: cq.Workplane,
    locations: List[Tuple[float, float]],
    nut: MetricNut,
    depth: float,
    *,
    tol_clearance: float = 0.2,
    tol_flats: float = 0.0,  # reduced tolerance for snug fit
    chamfer: float = 0.0,
    angle: float = 0.0,
):
    """
    Applies a hex nut pocket and clearance hole to a given Workplane at specified locations.
    The pocket is cut blind starting from `depth` inside the given Workplane.
    The clearance hole uses cutThruAll.
    An optional chamfer can be added to the clearance hole at the Workplane surface.
    An optional angle can rotate the hex nut around its center.
    """
    actual_clearance_dia = nut.clearance_dia + tol_clearance * 2
    circumscribed_dia = (nut.across_flats + tol_flats * 2) / (math.sqrt(3) / 2)

    res = wp
    if chamfer > 0:
        # Create chamfer by cutting a tapered hole from `chamfer` inside the face, expanding outwards
        res = (
            res.copyWorkplane(wp)
            .pushPoints(locations)
            .circle(actual_clearance_dia / 2 + chamfer)
            .cutBlind(-chamfer, taper=45)
        )

    # Use a sketch to allow rotating the hex nut profile
    # regularPolygon(angle=30) aligns the corners to the X axis matching wp.polygon default
    nut_sketch = cq.Sketch().regularPolygon(circumscribed_dia / 2, 6, angle=30 + angle)

    # Hex nut pocket (blind cut upwards from `depth` distance from the workplane face)
    res = (
        res.copyWorkplane(wp)
        .workplane(offset=-depth)
        .pushPoints(locations)
        .placeSketch(nut_sketch)
        .cutBlind(-nut.thickness)
    )
    # Clearance hole (cut through all)
    res = (
        res.copyWorkplane(wp)
        .pushPoints(locations)
        .circle(actual_clearance_dia / 2)
        .cutThruAll()
    )

    return res

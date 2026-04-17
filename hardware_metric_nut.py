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


def apply_hex_nut_tool(
    wp: cq.Workplane,
    locations: List[Tuple[float, float]],
    nut: MetricNut,
    depth: float,
    *,
    tol_clearance: float = 0.2,
    tol_flats: float = 0.0,  # reduced tolerance for snug fit
    chamfer: float = 0.0,
):
    """
    Applies a hex nut pocket and clearance hole to a given Workplane at specified locations.
    The pocket is cut blind starting from `depth` inside the given Workplane.
    The clearance hole uses cutThruAll.
    An optional chamfer can be added to the clearance hole at the Workplane surface.
    """
    actual_clearance_dia = nut.clearance_dia + tol_clearance * 2
    circumscribed_dia = (nut.across_flats + tol_flats * 2) / (math.sqrt(3) / 2)

    res = wp.tag("wp")
    if chamfer > 0:
        # Create chamfer by cutting a tapered hole from `chamfer` inside the face, expanding outwards
        res = (
            res.workplaneFromTagged("wp")
            .workplane(offset=-chamfer)
            .pushPoints(locations)
            .circle(actual_clearance_dia / 2)
            .cutBlind(chamfer, taper=-45)
        )

    # Hex nut pocket (blind cut upwards from `depth` distance from the workplane face)
    res = (
        res.workplaneFromTagged("wp")
        .workplane(offset=-depth)
        .pushPoints(locations)
        .polygon(6, circumscribed_dia)
        .cutBlind(-nut.thickness)
    )
    # Clearance hole (cut through all)
    res = (
        res.workplaneFromTagged("wp")
        .pushPoints(locations)
        .circle(actual_clearance_dia / 2)
        .cutBlind(-depth)
    )

    return res

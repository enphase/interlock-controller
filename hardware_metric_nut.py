import math

import cadquery as cq
from typing import NamedTuple, List, Tuple


class MetricNut(NamedTuple):
    """Nominal dimensions for standard metric hex nuts."""

    thread_size: str
    across_flats: float
    thickness: float
    clearance_dia: float


# Nominal dimensions from ISO/DIN standards for M3 hex nuts
M3_NUT = MetricNut(thread_size="M3", across_flats=5.5, thickness=2.4, clearance_dia=3.2)


def apply_hex_nut_tool(
    wp: cq.Workplane,
    locations: List[Tuple[float, float]],
    nut: MetricNut,
    pocket_depth: float,
    *,
    tol_clearance: float = 0.2,
    tol_flats: float = 0.0,  # reduced tolerance for snug fit
) -> cq.Workplane:
    """
    Applies a hex nut pocket and clearance hole to a given Workplane at specified locations.
    The pocket is cut blind, and the clearance hole uses cutThruAll.
    """
    actual_clearance_dia = nut.clearance_dia + tol_clearance * 2
    circumscribed_dia = (nut.across_flats + tol_flats * 2) / math.sqrt(3) / 2

    # Hex nut pocket (blind cut from the current workplane face)
    res = wp.pushPoints(locations).polygon(6, circumscribed_dia).cutBlind(-pocket_depth)

    # Clearance hole (cut through all)
    res = res.pushPoints(locations).circle(actual_clearance_dia / 2).cutThruAll()

    return res

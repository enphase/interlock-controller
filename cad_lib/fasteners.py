# Copyright 2026 Enphase Energy, Inc.
#
#    Licensed under the Apache License, Version 2.0 (the "License");
#    you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS,
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    See the License for the specific language governing permissions and
#    limitations under the License.

import math

import cadquery as cq
from typing import NamedTuple, List, Tuple


class MetricNut(NamedTuple):
    """Nominal dimensions for standard metric hex nuts."""

    thread_size: str
    nut_hex_across_flats: float
    nut_thickness: float
    clearance_dia: float
    countersink_depth: float

    def diameter(self) -> float:
        """Returns the circumscribed diameter (distance across corners)."""
        return self.nut_hex_across_flats / (math.sqrt(3) / 2)


# Nominal dimensions from ISO/DIN standards for M3 hex nuts
M3_NUT = MetricNut(
    thread_size="M3",
    nut_hex_across_flats=5.5,
    nut_thickness=2.4,
    clearance_dia=3.2,
    countersink_depth=1.7,
)
M4_NUT = MetricNut(
    thread_size="M4",
    nut_hex_across_flats=7.0,
    nut_thickness=3.2,
    clearance_dia=4.3,
    countersink_depth=2.3,
)


def cut_hex_nut_pocket(
    wp: cq.Workplane,
    locations: List[Tuple[float, float]],
    nut: MetricNut,
    depth: float = 0.0,
    *,
    tol_clearance: float = 0.2,
    tol_flats: float = -0.1,  # reduced tolerance for snug fit
    chamfer: float = 0.0,
    angle: float = 0.0,
):
    """
    Cuts a hex nut pocket and clearance hole into a workplane at specified locations.
    The pocket is cut blind starting from `depth` inside the given Workplane.
    The clearance hole uses cutThruAll.
    An optional chamfer can be added to the clearance hole at the Workplane surface.
    An optional angle can rotate the hex nut around its center.
    """
    actual_clearance_dia = nut.clearance_dia + tol_clearance * 2
    circumscribed_dia = (nut.nut_hex_across_flats + tol_flats * 2) / (math.sqrt(3) / 2)

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
        .cutBlind(-nut.nut_thickness)
    )
    # Clearance hole (cut through all)
    res = (
        res.copyWorkplane(wp)
        .pushPoints(locations)
        .circle(actual_clearance_dia / 2)
        .cutThruAll()
    )

    return res


def cut_countersink_hole(
    wp: cq.Workplane,
    locations: List[Tuple[float, float]],
    nut: MetricNut,
    *,
    tol_clearance: float = 0.2,
    tol_countersink: float = 0.2,
):
    """
    Cuts a countersink hole (typically 90 degrees for metric flat head screws)
    into a workplane at specified locations.
    The countersink is cut from the surface of the Workplane.
    """
    return (
        wp.copyWorkplane(wp)
        .pushPoints(locations)
        .cskHole(
            diameter=nut.clearance_dia + tol_clearance * 2,
            cskDiameter=nut.clearance_dia
            + 2 * (nut.countersink_depth + tol_countersink),
            cskAngle=90,
        )
    )

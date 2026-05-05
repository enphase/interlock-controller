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

import cadquery as cq
from typing import List, Tuple
from .fasteners import MetricNut, cut_hex_nut_pocket


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
    PANEL_CUTOUT_WIDTH = 27.3
    PANEL_CUTOUT_HEIGHT = 31.4
    PANEL_CUTOUT_RADIUS = 1.0
    HOLE_SPACING = 36.0

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


def cut_barrel_jack(
    wp: cq.Workplane, locations: List[Tuple[float, float]], *, tol: float = 0.0
) -> cq.Workplane:
    """
    Cuts a 11mm hole for panel-mount barrel jacks, with a 12.5mm flange and 14mm metric nut.
    """
    BARREL_JACK_DIA = 11.0

    return (
        wp.copyWorkplane(wp)
        .pushPoints(locations)
        .circle(BARREL_JACK_DIA / 2 + tol * 2)
        .cutBlind(until="next")
    )

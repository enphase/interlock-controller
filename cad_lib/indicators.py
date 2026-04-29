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
from typing import Tuple
from .fasteners import MetricNut, cut_hex_nut_pocket, M4_NUT

HOLE_PATTERN_L = 36.0
HOLE_PATTERN_W = 36.0


def cut_tower_light_mounting(
    wp: cq.Workplane,
    location: Tuple[float, float],
    depth: float,
    *,
    tol: float = 0.2,
) -> cq.Workplane:
    """
    Cuts the mounting holes for the tower light and wiring hole.
    """
    res = wp

    # Mounting hole pattern
    res = cut_hex_nut_pocket(
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

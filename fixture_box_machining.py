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
from pathlib import Path
from typing import Callable

from cadquery import cq


def build_box_machining_fixture(
    width: float,
    length: float,
    height: float,
    layer0_cutouts: Callable[[cq.Workplane], cq.Workplane],
    layer0_height: float,
    thickness: float = 3.0,
    infill_grid: int = 4,
) -> cq.Workplane:
    """Creates a semi-hollow box of total width x length x height.
    Of that total height, the layer0_height of it has cutouts defined as layer0_cutouts, eg for bosses.
    The remaining volume is hollow with a grid (with infill_grid rows / columns,
    so the number of cross-supports inclusive of exterior walls is infill_grid+1) and an X diagonal support,
    both walls of thickness.
    Thickness is also the thickness of the top face. The bottom face is entirely layer0.

    This is meant to be a fixturing mechanism to provide a solid block so the machining vises
    can clamp against the bottom of the box instead of against the thin walls.

    This also handles the case where height < layer0_height, in which case this just generates a plate of layer0_height.
    """

    # TODO IMPLEMENT ME


def layer0_cutouts_125_125(wp: cq.Workplane) -> cq.Workplane:
    """Generates cutouts for bosses in this box."""
    # one boss dead center
    CENTER_BOSS_DIAMETER = 20.0
    # threaded bosses in a + pattern, with this spacing between centers
    THREADED_BOSS_DIAMETER = 14.0
    THREADED_BOSS_SPACING = 110.6
    # corner bosses in an x pattern, with this x and y spacing between centers
    CORNER_BOSS_DIAMETER = 10.0
    CORNER_BOSS_SPACING = 119.3
    BOSS_HEIGHT = 8.0

    # TODO IMPLEMENT ME
    return wp


if __name__ == "__main__":
    Path("generated").mkdir(parents=True, exist_ok=True)
    cq.exporters.export(
        build_box_machining_fixture(
            125.0, 125.0, 73.0, layer0_cutouts_125_125, 8.0, thickness=3.0
        ),
        "generated/fixture_relay_enclosure.stl",
    )
    cq.exporters.export(
        build_box_machining_fixture(
            125.0, 125.0, 0.0, layer0_cutouts_125_125, 3.0, thickness=3.0
        ),
        "generated/fixture_relay_enclosure.stl",
    )

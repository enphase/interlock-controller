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
from pathlib import Path
from typing import Callable

import cadquery as cq


def build_box_machining_fixture(
    width: float,
    length: float,
    height: float,
    layer0_cutouts: Callable[[cq.Workplane], cq.Sketch],
    layer0_height: float,
    thickness: float = 2.0,
    infill_grid: int = 4,
) -> cq.Workplane:
    """Creates a semi-hollow box of total width x length x height.
    Of that total height, the layer0_height of it has cutouts defined as layer0_cutouts, eg for bosses.
    The remaining volume is hollow with a grid (with infill_grid rows / columns,
    so the number of cross-supports inclusive of exterior walls is infill_grid+1) and an X diagonal support,
    both walls of thickness.
    Thickness is also the thickness of the top face and the bottom face above layer0_height

    This is meant to be a fixturing mechanism to provide a solid block so the machining vises
    can clamp against the bottom of the box instead of against the thin walls.

    This also handles the case where height < layer0_height, in which case this just generates a plate of layer0_height.
    """
    actual_height = max(height, layer0_height)

    # Layer 0: solid base with cutouts
    cutout_sketch = layer0_cutouts(cq.Workplane("XY"))
    layer0 = cq.Workplane("XY").rect(width, length).extrude(layer0_height)
    layer0 = (
        layer0.faces(">Z")
        .workplane()
        .placeSketch(cutout_sketch)
        .cutBlind(-layer0_height)
    )

    infill_height = actual_height - layer0_height - 2 * thickness
    if infill_height <= 0:
        return layer0

    # Bottom plate above layer0
    infill_base_z = layer0_height + thickness

    # Infill structure: outer walls + grid + X diagonal, all of `thickness`
    # Build as a 2D sketch and extrude
    infill_sketch = cq.Sketch()

    # Outer walls: rect shell
    infill_sketch = infill_sketch.rect(width, length).rect(
        width - 2 * thickness, length - 2 * thickness, mode="s"
    )

    # Grid cross-supports: infill_grid divisions means (infill_grid - 1) internal lines
    # along X (vertical lines at constant x)
    for i in range(1, infill_grid):
        x = -width / 2 + i * (width / infill_grid)
        infill_sketch = infill_sketch.push([(x, 0)]).rect(thickness, length)
    # along Y (horizontal lines at constant y)
    for i in range(1, infill_grid):
        y = -length / 2 + i * (length / infill_grid)
        infill_sketch = infill_sketch.push([(0, y)]).rect(width, thickness)

    infill_sketch = infill_sketch.clean()

    infill = (
        cq.Workplane("XY")
        .workplane(offset=infill_base_z)
        .placeSketch(infill_sketch)
        .extrude(infill_height)
    )

    # X diagonal supports
    # Diagonal from (-width/2, -length/2) to (width/2, length/2)
    diag_length = math.sqrt(width**2 + length**2)
    diag_angle = math.degrees(math.atan2(length, width))

    for angle in [diag_angle, -diag_angle]:
        diagonal = (
            cq.Workplane("XY")
            .workplane(offset=infill_base_z)
            .rect(diag_length, thickness)
            .extrude(infill_height)
        )
        diagonal = diagonal.rotate((0, 0, 0), (0, 0, 1), angle)
        # Clip to bounding box
        clip_box = (
            cq.Workplane("XY")
            .workplane(offset=infill_base_z)
            .rect(width, length)
            .extrude(infill_height)
        )
        diagonal = diagonal.intersect(clip_box)
        infill = infill.union(diagonal)

    # Bottom face above layer0 + top cap
    bottom_cap = (
        cq.Workplane("XY")
        .workplane(offset=layer0_height)
        .rect(width, length)
        .extrude(thickness)
    )
    top_cap = (
        cq.Workplane("XY")
        .workplane(offset=actual_height - thickness)
        .rect(width, length)
        .extrude(thickness)
    )

    return layer0.union(bottom_cap).union(infill).union(top_cap)


def layer0_cutouts_125_125(wp: cq.Workplane) -> cq.Sketch:
    """Generates a sketch of cutouts for bosses in this box."""
    # one boss dead center
    CENTER_BOSS_DIAMETER = 20.0
    # threaded bosses in a + pattern, with this spacing between centers
    THREADED_BOSS_DIAMETER = 14.0
    THREADED_BOSS_SPACING = 110.6
    # corner bosses in an x pattern, with this x and y spacing between centers
    CORNER_BOSS_DIAMETER = 10.0
    CORNER_BOSS_SPACING = 119.3

    s = THREADED_BOSS_SPACING / 2
    c = CORNER_BOSS_SPACING / 2

    sketch = (
        cq.Sketch()
        # Center boss
        .circle(CENTER_BOSS_DIAMETER / 2)
        # Threaded bosses in + pattern
        .reset()
        .push([(s, 0), (-s, 0), (0, s), (0, -s)])
        .circle(THREADED_BOSS_DIAMETER / 2)
        # Corner bosses in X pattern
        .reset()
        .push([(c, c), (c, -c), (-c, c), (-c, -c)])
        .circle(CORNER_BOSS_DIAMETER / 2)
    )
    return sketch


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
        "generated/fixture_relay_enclosure_plate.stl",
    )

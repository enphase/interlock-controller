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

import cadquery as cq

from cad_lib.power_entry import cut_719w_power_entry
from cad_lib.connectors import cut_m12_connector_holes
from cad_lib.fasteners import M3_NUT, cut_hex_nut_pocket
from cad_lib.indicators import cut_tower_light_mounting

# --- Parameters ---

# Note on Coordinate System:
# The box is centered at the origin (X, Y).
# Z=0 is the printbed (bottom face of the print) AND the external face of the plate.
# +Z goes up and represents going into the enclosure.
# The plate occupies Z=[0, plate_thickness].

# Plate dimensions
CUTOUT_WIDTH = 40.0
CUTOUT_RADIUS = 10.0

FLANGE_MARGIN = 4.0

# Hex nut flanges
HEX_NUT = M3_NUT
NUT_DEPTH = 1.5
HEX_FLANGE_RADIUS = 8.0

M12_CONNECTOR_SPACING = 22.0

VERSION = "v1.2"

# Emboss Parameters (Extruded upwards from the inside face)
EMBOSS_THICKNESS = 0.4
EMBOSS_WIDTH = 0.8


def make_d_flange_sketch(radius: float, extension: float, dir_x: float) -> cq.Sketch:
    """
    Creates a reusable 2D sketch for a D-shaped flange.
    It is a round rect on the outside (180 degrees) and a square/rect on the inside.
    dir_x: 1 points right (+x), -1 points left (-x)
    """
    return (
        cq.Sketch()
        .circle(radius)
        .push([(-dir_x * extension / 2, 0)])
        .rect(extension, radius * 2)
    )


def build_base_plate(
    length: float,
    width: float,
    cutout_radius: float,
    thickness: float = 2.5,
    *,
    screw_pattern_length_offset: float = 4.0,
    screw_pattern_width_offset: float = -4.0,
    add_cutout_emboss: bool = True,
    version_text: str = "",
) -> cq.Workplane:
    """
    Builds the base plate with screw flanges and optional cutout outline emboss.
    """
    # 1. Create the main plate
    plate = (
        cq.Workplane("XY")
        .rect(length + 2 * FLANGE_MARGIN, width + 2 * FLANGE_MARGIN)
        .extrude(thickness)
        .edges("|Z")
        .fillet(cutout_radius + FLANGE_MARGIN)
    )

    # 2. Add D-flanges for the hex nuts
    screw_pattern_length = length + screw_pattern_length_offset * 2
    screw_pattern_width = width + screw_pattern_width_offset * 2
    screw_locations = [
        (screw_pattern_length / 2, screw_pattern_width / 2),
        (screw_pattern_length / 2, -screw_pattern_width / 2),
        (-screw_pattern_length / 2, screw_pattern_width / 2),
        (-screw_pattern_length / 2, -screw_pattern_width / 2),
    ]
    hex_flange_radius = HEX_FLANGE_RADIUS
    for loc in screw_locations:
        dir_x = 1 if loc[0] > 0 else -1
        # Extension ensures it deeply overlaps into the main plate for unioning
        sketch = make_d_flange_sketch(
            hex_flange_radius,
            cutout_radius + screw_pattern_length_offset,
            dir_x,
        )
        flange_wp = (
            cq.Workplane("XY")
            .center(loc[0], loc[1])
            .placeSketch(sketch)
            .extrude(thickness)
        )
        plate = plate.union(flange_wp)

    # 3. Cut the hex nut slots and clearance holes
    # We start from the bottom face (<Z) to pocket the nut upward, then cut clearance through all
    plate = cut_hex_nut_pocket(
        plate.faces("<Z"),
        screw_locations,
        HEX_NUT,
        depth=NUT_DEPTH,
        chamfer=0.5,
    )

    # 4. Add Cutout Outline Emboss
    if add_cutout_emboss:
        outer_w = length + EMBOSS_WIDTH
        outer_h = width + EMBOSS_WIDTH
        outer_r = cutout_radius + EMBOSS_WIDTH / 2

        inner_w = length - EMBOSS_WIDTH
        inner_h = width - EMBOSS_WIDTH
        inner_r = cutout_radius - EMBOSS_WIDTH / 2

        cutout_emboss_base = (
            cq.Workplane("XY")
            .workplane(offset=thickness)
            .rect(outer_w, outer_h)
            .extrude(EMBOSS_THICKNESS)
            .edges("|Z")
            .fillet(outer_r)
        )

        cutout_emboss_hole = (
            cq.Workplane("XY")
            .workplane(
                offset=thickness - 0.1
            )  # Offset lower to avoid coincident face issues
            .rect(inner_w, inner_h)
            .extrude(EMBOSS_THICKNESS + 0.2)
            .edges("|Z")
            .fillet(inner_r)
        )

        cutout_emboss = cutout_emboss_base.cut(cutout_emboss_hole)
        plate = plate.union(cutout_emboss)

    # 5. Version Text Emboss
    if version_text:
        text_x = length / 2 - FLANGE_MARGIN - cutout_radius
        text_y = -width / 2 + FLANGE_MARGIN

        text_emboss = (
            cq.Workplane("XY")
            .workplane(offset=thickness)
            .center(text_x, text_y)
            .text(
                version_text,
                fontsize=6.0,
                distance=EMBOSS_THICKNESS,
                kind="bold",
                halign="right",
                valign="bottom",
            )
        )
        plate = plate.union(text_emboss)

    return plate


def build_bottom_cutout_plate() -> cq.Workplane:
    cutout_length = 116.0

    # M12 Connectors
    num_connectors = 3
    connector_locations = [
        (-cutout_length / 2 + M12_CONNECTOR_SPACING * (i + 0.5), 0)
        for i in range(num_connectors)
    ]

    # AC Power Entry Module
    power_locations = [(cutout_length / 2 - 25.0, 0)]

    plate = build_base_plate(
        length=cutout_length,
        width=CUTOUT_WIDTH,
        cutout_radius=CUTOUT_RADIUS,
        add_cutout_emboss=True,
        version_text=f"BOT {VERSION}",
    )

    # 5. Cut the M12 connector holes
    # We start from the bottom face (<Z) and cut through all downwards
    # In order to place the chamfer on the exterior face (Z=0), we pass in the bottom face
    plate = cut_m12_connector_holes(plate.faces("<Z").workplane(), connector_locations)

    # 6. Cut the 719W AC Power Entry Module cutout
    plate = cut_719w_power_entry(
        plate.faces("<Z"),
        power_locations,
        HEX_NUT,
        depth=NUT_DEPTH,
        chamfer=0.5,
    )

    return plate


def build_top_cutout_plate() -> cq.Workplane:
    cutout_length = 116.0

    # M12 Connectors
    num_connectors = 2
    connector_locations = [
        (cutout_length / 2 - M12_CONNECTOR_SPACING * (i + 0.5), 0)
        for i in range(num_connectors)
    ]

    # 5. Cut the M12 connector holes
    # We start from the bottom face (<Z) and cut through all downwards
    # In order to place the chamfer on the exterior face (Z=0), we pass in the bottom face
    plate = build_base_plate(
        length=cutout_length,
        width=CUTOUT_WIDTH,
        cutout_radius=CUTOUT_RADIUS,
        add_cutout_emboss=True,
        version_text=f"TOP {VERSION}",
    )

    plate = cut_m12_connector_holes(plate.faces("<Z").workplane(), connector_locations)

    plate = cut_tower_light_mounting(
        plate.faces("<Z").workplane(),
        (-(cutout_length / 2 - CUTOUT_RADIUS - 18), 0),
        depth=NUT_DEPTH,
    )

    return plate


def build_side_cutout_plate() -> cq.Workplane:
    cutout_length = 216.0

    # M12 Connectors
    num_connectors = 4
    connector_locations = [
        (cutout_length / 2 - M12_CONNECTOR_SPACING * (i + 0.5), 0)
        for i in range(num_connectors)
    ]

    # 5. Cut the M12 connector holes
    # We start from the bottom face (<Z) and cut through all downwards
    # In order to place the chamfer on the exterior face (Z=0), we pass in the bottom face
    plate = build_base_plate(
        length=cutout_length,
        width=CUTOUT_WIDTH,
        cutout_radius=CUTOUT_RADIUS,
        add_cutout_emboss=True,
        version_text=f"SIDE {VERSION}",
    )

    plate = cut_m12_connector_holes(plate.faces("<Z").workplane(), connector_locations)

    return plate


# --- Export ---
if __name__ == "__main__":
    Path("generated").mkdir(parents=True, exist_ok=True)
    cq.exporters.export(
        build_top_cutout_plate(), "generated/connector_plate_top_116_40.stl"
    )
    cq.exporters.export(
        build_bottom_cutout_plate(), "generated/connector_plate_bottom_116_40.stl"
    )
    cq.exporters.export(
        build_side_cutout_plate(), "generated/connector_plate_side_216_40.stl"
    )

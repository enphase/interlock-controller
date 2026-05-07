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

from cad_lib.fasteners import M4_NUT, cut_countersink_hole, cut_hex_nut_pocket


def build_vertical_din_bracket() -> cq.Workplane:
    """Generates a bracket-like structures, that screws onto a base plate (on the xy plane)
    and provides a plate (on the xz plane, aligned to the +y side of the base plate)
    with a DIN rail mounting pattern.

    The base plate has screws in a + pattern, and has countersunk clearance holes (the part
    this screws to is threaded).

    The DIN plate has hex nut sockets, which a DIN rail screws into.

    The two are joined both by a direct right-angle join, as well as fillets on both sides of the DIN plate.
    """
    BASE_WIDTH = 125  # dimension on the x-axis
    BASE_LENGTH = 125  # dimension on the y-axis
    BASE_THICKNESS = 3.0
    BASE_SCREW_SPACING = 100.0  # spacing between centers, + pattern
    BASE_SCREW = M4_NUT

    DIN_BASE_THICKNESS = 5.0
    DIN_BASE_WIDTH = 100.0  # dimension on the x-axis
    DIN_BASE_HEIGHT = 75.0  # dimension on the z-axis
    DIN_BASE_SCREW_SPACING = (
        50.0  # spacing between centers, centered on center of din base
    )
    DIN_BASE_SCREW = M4_NUT
    DIN_BASE_FILLET_THICKNESS = 3.0
    DIN_BASE_FILLET_RADIUS = 30.0

    # Base plate (horizontal, XY plane)
    base = cq.Workplane("XY").rect(BASE_WIDTH, BASE_LENGTH).extrude(BASE_THICKNESS)

    # Cut countersunk holes in + pattern on the bottom face
    s = BASE_SCREW_SPACING / 2
    base_screw_locations = [(s, 0), (-s, 0), (0, s), (0, -s)]
    base = cut_countersink_hole(
        base.faces(">Z").workplane(), base_screw_locations, BASE_SCREW
    )

    # DIN plate (vertical, XZ plane, at +Y edge of base)
    # Position it at y = BASE_LENGTH/2, extending from z=BASE_THICKNESS upward
    din_plate = (
        cq.Workplane("XZ")
        .workplane(offset=-BASE_LENGTH / 2)  # moves in -y for some reason
        .center(0, DIN_BASE_HEIGHT / 2 + BASE_THICKNESS)
        .rect(DIN_BASE_WIDTH, DIN_BASE_HEIGHT)
        .extrude(DIN_BASE_THICKNESS)
    )

    # Cut hex nut pockets on the back face (-Y face) of the DIN plate
    # The DIN rail screws come from the front (+Y) and thread into nuts on the back
    # DIN rail mounting: two screws vertically spaced, centered on the plate
    din_screw_spacing = DIN_BASE_SCREW_SPACING / 2
    din_screw_locations = [(0, din_screw_spacing), (0, -din_screw_spacing)]
    din_plate = cut_hex_nut_pocket(
        din_plate.faces("<Y").workplane(),
        din_screw_locations,
        DIN_BASE_SCREW,
        depth=DIN_BASE_THICKNESS - DIN_BASE_SCREW.nut_thickness,
    )

    # Union base and DIN plate
    bracket = base.union(din_plate)

    # Add rounded fillet supports as extruded arcs
    # Create a quarter-circle profile and extrude it along X at both edges
    # Fillets support the DIN plate from below, curving from base up to the back of DIN plate
    for x_sign in [-1, 1]:
        # Start position for the fillet (inward from edge)
        x_start = x_sign * (DIN_BASE_WIDTH / 2 - DIN_BASE_FILLET_THICKNESS)

        # Create quarter-circle arc in YZ plane
        # Arc from base (y - radius, z) up and forward to DIN plate back (y, z + radius)
        y_base = BASE_LENGTH / 2 - DIN_BASE_THICKNESS
        z_base = BASE_THICKNESS
        fillet_support = (
            cq.Workplane("YZ")
            .workplane(offset=x_start)
            .moveTo(y_base - DIN_BASE_FILLET_RADIUS, z_base)
            .radiusArc(
                (y_base, z_base + DIN_BASE_FILLET_RADIUS),
                -DIN_BASE_FILLET_RADIUS,
            )
            .lineTo(y_base, z_base)
            .close()
            .extrude(DIN_BASE_FILLET_THICKNESS * x_sign)
        )
        bracket = bracket.union(fillet_support)

    return bracket


if __name__ == "__main__":
    Path("generated").mkdir(parents=True, exist_ok=True)
    cq.exporters.export(
        build_vertical_din_bracket(),
        "generated/vertical_din_adapter.stl",
    )

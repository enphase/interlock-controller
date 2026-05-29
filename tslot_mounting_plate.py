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
from typing import List, Tuple, Callable

import cadquery as cq

from cad_lib.fasteners import (
    M3_NUT,
    M4_NUT,
    cut_countersink_hole,
    cut_hex_nut_pocket,
    MetricNut,
)
from tslot_nut import TSlotProfile, PROFILE_4545


def build_tslot_mounting_adapter_plate(
    width: float,
    height: float,
    payload_mount_locations: List[Tuple[float, float]],
    payload_screw: MetricNut,
    *,
    payload_hole_tool: Callable = cut_countersink_hole,
    thickness: float = 3.0,
    rail_mounting_x: float = 0.0,
    fillet: float = 0.0,
) -> cq.Workplane:
    """Generates an adapter plate, that some object with back-side mounting holes attaches to,
    and provides front-side mounting holes to allow it to be mounted to a t-slot rail.

    The plate is of width x height, centered at (0, 0) on the XY plane.
    The payload this adapts to is installed from +Z, screwed in from -Z.
    This has holes for the payload at payload_mount_locations.

    This has two stubs, centered at x=rail_mounting_x, sticking out from the top and bottom,
    to attach to a rail/backing piece in -Z, screwed in from +Z.
    The hole for the rail is countersunk.
    """
    RAIL_MOUNTING_SCREW = M4_NUT
    RAIL_MOUNTING_OFFSET = 8.0  # distance from edge of plate to mounting hole
    RAIL_MOUNTING_STUB_DIAMETER = 16.0

    s = (
        cq.Sketch()
        .rect(width, height)
        .push(
            [
                (rail_mounting_x, height / 2 + RAIL_MOUNTING_OFFSET / 2),
                (rail_mounting_x, -height / 2 - RAIL_MOUNTING_OFFSET / 2),
            ]
        )
        .rect(RAIL_MOUNTING_STUB_DIAMETER, RAIL_MOUNTING_OFFSET)
        .reset()
        .push(
            [
                (rail_mounting_x, height / 2 + RAIL_MOUNTING_OFFSET),
                (rail_mounting_x, -height / 2 - RAIL_MOUNTING_OFFSET),
            ]
        )
        .circle(RAIL_MOUNTING_STUB_DIAMETER / 2)
        .clean()
    )
    base = cq.Workplane("XY").placeSketch(s).extrude(thickness / 2, both=True)
    # Subtract a tiny amount to avoid CAD kernel issues with fillets that perfectly meet other geometry
    base = base.newObject(base.edges("|Z").vals()).fillet(fillet - 0.001)

    # Holes for mounting the payload on the bottom face (<Z)
    flipped_mount_locations = [(x, -y) for x, y in payload_mount_locations]
    base = payload_hole_tool(
        base.faces("<Z").workplane(), flipped_mount_locations, payload_screw
    )

    # Countersunk holes for mounting to the rail on the top face (>Z)
    stub_locations = [
        (rail_mounting_x, height / 2 + RAIL_MOUNTING_OFFSET),
        (rail_mounting_x, -height / 2 - RAIL_MOUNTING_OFFSET),
    ]
    base = cut_countersink_hole(
        base.faces(">Z").workplane(), stub_locations, RAIL_MOUNTING_SCREW
    )

    return base


def build_tslot_mounting_plate(
    tslot_profile: TSlotProfile,
    screw: MetricNut,
    width: float,
    height: float,
    *,
    thickness: float = 3.0,
    clearance: float = 0.2,
) -> cq.Workplane:
    """Generates a mounting plate of width x height, symmetric around the origin.
    The mounting hole is a countersunk hole for screw, at the origin, inserted from -Z.
    Z=0 is the face of the rail, with the thickness extending into -Z.

    This can be used to, for example, mount cable organizer clips, adhesively attached to the plate,
    to the t-slot rail.

    To prevent rotation, this has an extrusion the width of tslot_profile.slot_width
    and height 1/3 of the slot_depth, extending into +Z
    """
    tab_z = tslot_profile.slot_depth / 3

    # Main plate body: from Z=-thickness to Z=0
    base = (
        cq.Workplane("XY")
        .workplane(offset=-thickness)
        .rect(width, height)
        .extrude(thickness)
    )

    # Anti-rotation tab: slot_width x height in XY, from Z=0 to Z=+tab_z
    tab = (
        cq.Workplane("XY")
        .rect(tslot_profile.slot_width - clearance * 2, height)
        .extrude(tab_z)
    )
    base = base.union(tab)

    # Countersunk hole at origin, inserted from -Z face
    base = cut_countersink_hole(
        base.faces("<Z").workplane(),
        [(0, 0)],
        screw,
    )

    return base


if __name__ == "__main__":
    Path("generated").mkdir(parents=True, exist_ok=True)

    cq.exporters.export(
        build_tslot_mounting_adapter_plate(
            76.0,
            76.0,
            [(-31, 20.5), (-31, -10.5), (31, -20.5), (31, 10.5)],
            M4_NUT,
            rail_mounting_x=-(76 - 45) / 2,
            fillet=4.0,
        ),
        "generated/adapter_idec76_m4cs.stl",
    )
    cq.exporters.export(
        build_tslot_mounting_adapter_plate(
            76.0,
            140.0,
            [(-31, 52), (-31, -42), (31, -52), (31, 42)],
            M4_NUT,
            rail_mounting_x=-(76 - 45) / 2,
            fillet=4.0,
        ),
        "generated/adapter_idec140_m4cs.stl",
    )
    cq.exporters.export(
        build_tslot_mounting_adapter_plate(
            47,
            115.0,
            [(-47 / 2 + 9, -105 / 2 + 69 + 5), (47 / 2 - 9, -105 / 2 + 16 + 5)],
            M3_NUT,
            thickness=5.0,  # accommodate a M3x8 screw
            fillet=4.0,
            payload_hole_tool=lambda wp, locs, screw: cut_hex_nut_pocket(
                wp, locs, screw, depth=0
            ),
        ),
        "generated/adapter_doorsense_m4cs.stl",
    )

    cq.exporters.export(
        build_tslot_mounting_plate(
            PROFILE_4545,
            M4_NUT,
            45.0,
            20.0,
        ),
        "generated/tslot_mounting_plate_4545_m4.stl",
    )

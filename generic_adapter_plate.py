from typing import List, Tuple, Callable

import cadquery as cq

from cad_lib.fasteners import (
    M3_NUT,
    M4_NUT,
    cut_countersink_hole,
    cut_hex_nut_pocket,
    MetricNut,
)


def build_adapter_plate(
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
    """Generates an adapter plate, of width x height, centered at (0, 0) on the XY plane.
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


if __name__ == "__main__":
    cq.exporters.export(
        build_adapter_plate(
            76.0,
            76.0,
            [(-31, 20.5), (-31, -10.5), (31, -20.5), (31, 10.5)],
            M4_NUT,
            rail_mounting_x=-(76 - 45) / 2,
            fillet=4.0,
        ),
        "idec76_4545_adapter.stl",
    )
    cq.exporters.export(
        build_adapter_plate(
            76.0,
            140.0,
            [(-31, 52), (-31, -42), (31, -52), (31, 42)],
            M4_NUT,
            rail_mounting_x=-(76 - 45) / 2,
            fillet=4.0,
        ),
        "idec140_4545_adapter.stl",
    )
    cq.exporters.export(
        build_adapter_plate(
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
        "doorsense_adapter.stl",
    )

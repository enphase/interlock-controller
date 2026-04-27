from typing import List, Tuple

import cadquery as cq

from hardware_metric_nut import (
    M4_NUT,
    apply_countersink_hole,
    MetricNut,
)


def build_adapter_plate(
    width: float,
    height: float,
    mount_locations: List[Tuple[float, float]],
    screw: MetricNut,
    *,
    back_mounting_x: float = 0.0,
) -> cq.Workplane:
    """Generates an adapter plate, of width x height, centered at (0, 0) on the XY plane.
    The piece this adapts to is threaded and installed from +Z, screwed in from -Z.
    This has countersunk holes for the piece at mount_locations.

    This has two stubs, centered at x=back_mounting_x, sticking out from the top and bottom,
    to attach to a (threaded) backing piece in -Z, screwed in from +Z.
    The hole is countersunk.
    """
    THICKNESS = 4.0  # plate thickness
    BACK_MOUNTING_SCREW = M4_NUT
    BACK_MOUNTING_OFFSET = 12.0  # distance from edge of plate to mounting hole
    BACK_MOUNTING_STUB_DIAMETER = 12.0

    stub_len = BACK_MOUNTING_OFFSET
    stub_radius = BACK_MOUNTING_STUB_DIAMETER / 2

    s = (
        cq.Sketch()
        .rect(width, height)
        .push(
            [
                (back_mounting_x, height / 2 + stub_len / 2),
                (back_mounting_x, -height / 2 - stub_len / 2),
            ]
        )
        .rect(stub_radius * 2, stub_len)
        .reset()
        .push(
            [
                (back_mounting_x, height / 2 + stub_len),
                (back_mounting_x, -height / 2 - stub_len),
            ]
        )
        .circle(stub_radius)
        .clean()
    )

    base = cq.Workplane("XY").placeSketch(s).extrude(THICKNESS / 2, both=True)

    # The piece this adapts to is installed from +Z, screwed in from -Z
    # Countersunk holes on the bottom face (<Z)
    flipped_mount_locations = [(x, -y) for x, y in mount_locations]
    bottom_wp = base.faces("<Z").workplane()
    base = apply_countersink_hole(bottom_wp, flipped_mount_locations, screw)

    # Stubs attached to backing piece in -Z, screwed in from +Z
    # Countersunk holes on the top face (>Z)
    stub_locations = [
        (back_mounting_x, height / 2 + BACK_MOUNTING_OFFSET),
        (back_mounting_x, -height / 2 - BACK_MOUNTING_OFFSET),
    ]
    top_wp = base.faces(">Z").workplane()
    base = apply_countersink_hole(top_wp, stub_locations, BACK_MOUNTING_SCREW)

    return base


if __name__ == "__main__":
    cq.exporters.export(
        build_adapter_plate(
            76.0,
            76.0,
            [(-31, 20.5), (-31, -10.5), (31, -20.5), (31, 10.5)],
            M4_NUT,
            back_mounting_x=-(76 - 45) / 2,
        ),
        "idec76_4545_adapter.stl",
    )

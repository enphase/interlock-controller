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
    thickness: float = 3.0,
    back_mounting_x: float = 0.0,
    fillet: float = 0.0,
) -> cq.Workplane:
    """Generates an adapter plate, of width x height, centered at (0, 0) on the XY plane.
    The piece this adapts to is threaded and installed from +Z, screwed in from -Z.
    This has countersunk holes for the piece at mount_locations.

    This has two stubs, centered at x=back_mounting_x, sticking out from the top and bottom,
    to attach to a (threaded) backing piece in -Z, screwed in from +Z.
    The hole is countersunk.
    """
    BACK_MOUNTING_SCREW = M4_NUT
    BACK_MOUNTING_OFFSET = 8.0  # distance from edge of plate to mounting hole
    BACK_MOUNTING_STUB_DIAMETER = 16.0

    s = (
        cq.Sketch()
        .rect(width, height)
        .push(
            [
                (back_mounting_x, height / 2 + BACK_MOUNTING_OFFSET / 2),
                (back_mounting_x, -height / 2 - BACK_MOUNTING_OFFSET / 2),
            ]
        )
        .rect(BACK_MOUNTING_STUB_DIAMETER, BACK_MOUNTING_OFFSET)
        .reset()
        .push(
            [
                (back_mounting_x, height / 2 + BACK_MOUNTING_OFFSET),
                (back_mounting_x, -height / 2 - BACK_MOUNTING_OFFSET),
            ]
        )
        .circle(BACK_MOUNTING_STUB_DIAMETER / 2)
        .clean()
    )
    base = cq.Workplane("XY").placeSketch(s).extrude(thickness / 2, both=True)
    # Subtract a tiny amount to avoid CAD kernel issues with fillets that perfectly meet other geometry
    base = base.newObject(base.edges("|Z").vals()).fillet(fillet - 0.001)

    # Countersunk holes for mounting the adapted piece on the bottom face (<Z)
    flipped_mount_locations = [(x, -y) for x, y in mount_locations]
    base = apply_countersink_hole(
        base.faces("<Z").workplane(), flipped_mount_locations, screw
    )

    # Countersunk holes for mounting to the backing piece on the top face (>Z)
    stub_locations = [
        (back_mounting_x, height / 2 + BACK_MOUNTING_OFFSET),
        (back_mounting_x, -height / 2 - BACK_MOUNTING_OFFSET),
    ]
    base = apply_countersink_hole(
        base.faces(">Z").workplane(), stub_locations, BACK_MOUNTING_SCREW
    )

    return base


if __name__ == "__main__":
    cq.exporters.export(
        build_adapter_plate(
            76.0,
            76.0,
            [(-31, 20.5), (-31, -10.5), (31, -20.5), (31, 10.5)],
            M4_NUT,
            back_mounting_x=-(76 - 45) / 2,
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
            back_mounting_x=-(76 - 45) / 2,
            fillet=4.0,
        ),
        "idec140_4545_adapter.stl",
    )

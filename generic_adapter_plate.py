from typing import List, Tuple

import cadquery as cq

from hardware_metric_nut import M4_NUT, apply_hex_nut_tool, MetricNut


def build_adapter_plate(
    width: float,
    height: float,
    mount_locations: List[Tuple[float, float]],
    screw: MetricNut,
    *,
    back_mounting_x: float = 0.0,
) -> cq.Workplane:
    """Generates an adapter plate, of width x height, centered at (0, 0) on the XY plane.
    The piece this adapts to is installed from +Z and has threads, screwed in from -Z.
    This has holes for the piece at mount_locations.

    This has two stubs, centered at x=back_mounting_x, sticking out from the top and bottom,
    to attach to a backing piece in -Z, screwed in from +Z.
    """
    THICKNESS = 4.0  # plate thickness
    BACK_MOUNTING_SCREW = M4_NUT
    BACK_MOUNTING_OFFSET = 12.0  # distance from edge of plate to mounting hole
    BACK_MOUNTING_STUB_DIAMETER = 8.0

    # implement me


if __name__ == "__main__":
    cq.exporters.export(
        build_adapter_plate(
            76.0,
            76.0,
            [(-31, -10.5), (31, 20.5), (-31, -20.5), (-31, -10.5)],
            M4_NUT,
            back_mounting_x=-(76 - 45) / 2,
        ),
        "idec_76_adapter_plate.stl",
    )

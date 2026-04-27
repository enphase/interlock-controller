from typing import List, Tuple

import cadquery as cq

from hardware_metric_nut import M4_NUT, apply_hex_nut_tool, MetricNut


def build_adapter_plate(
    width: float,
    height: float,
    mount_locations: List[Tuple[float, float]],
    screw: MetricNut,
) -> cq.Workplane:
    BACK_MOUTING_SCREW = M4_NUT

    # implement me


if __name__ == "__main__":
    cq.exporters.export(
        build_adapter_plate(76.0, 76.0, [], M4_NUT), "idec_76_adapter_plate.stl"
    )

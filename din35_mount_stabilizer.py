import math
import cadquery as cq
from typing import NamedTuple

from hardware_metric_nut import M4_NUT, MetricNut, apply_hex_nut_tool


def build_din35_stabilizer() -> cq.Workplane:
    width = 35.0  # width of DIN rail
    length = 60.0  # two perforations
    height = 6.0  # height of screw boss of the box
    nut_spacing = 10.0 + 4  # spacing between perforations plus screw diameter

    # Base block
    stabilizer = cq.Workplane("XY").box(length, width, height).edges("|Z").fillet(4.0)

    # We want the screws to come from the top, through the clearance holes,
    # and thread into nuts which are inserted from the bottom.
    top_face = stabilizer.faces(">Z").workplane()

    locations = [
        (-nut_spacing / 2, 0),
        (nut_spacing / 2, 0),
    ]

    # Apply the M4 hex nut tool
    # depth = height will make the pocket start at the bottom face and cut upwards into the part
    stabilizer = apply_hex_nut_tool(
        top_face,
        locations,
        nut=M4_NUT,
        depth=height - M4_NUT.thickness,
    )

    return stabilizer


if __name__ == "__main__":
    cq.exporters.export(build_din35_stabilizer(), "din35_stabilizer.stl")

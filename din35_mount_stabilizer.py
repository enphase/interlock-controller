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

from cad_lib.fasteners import M4_NUT, cut_hex_nut_pocket


def build_din35_stabilizer() -> cq.Workplane:
    nut_spacing = 7.0 + 4  # spacing between perforations plus screw diameter
    width = 35.0  # width of DIN rail
    length = nut_spacing + 8.0 * 2
    height = 6.0  # height of screw boss of the box

    # Base block
    stabilizer = cq.Workplane("XY").box(length, width, height).edges("|Z").fillet(4.0)

    # We want the screws to come from the top, through the clearance holes,
    # and thread into nuts which are inserted from the bottom.
    top_face = stabilizer.faces(">Z").workplane()

    locations = [
        (-nut_spacing / 2, 0),
        (nut_spacing / 2, 0),
    ]

    # Cut the M4 hex nut pockets
    # depth = height will make the pocket start at the bottom face and cut upwards into the part
    stabilizer = cut_hex_nut_pocket(
        top_face,
        locations,
        nut=M4_NUT,
        depth=height - M4_NUT.nut_thickness,
        angle=30,
    )

    return stabilizer


if __name__ == "__main__":
    Path("generated").mkdir(parents=True, exist_ok=True)
    cq.exporters.export(build_din35_stabilizer(), "generated/din35_stabilizer.stl")

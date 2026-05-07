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

from cad_lib.fasteners import M4_NUT


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
    DIN_BASE_FILLET_RADIUS = 20.0


if __name__ == "__main__":
    Path("generated").mkdir(parents=True, exist_ok=True)
    cq.exporters.export(
        build_vertical_din_bracket(),
        "generated/vertical_din_adapter.stl",
    )

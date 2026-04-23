import math
import cadquery as cq
from typing import NamedTuple

from hardware_metric_nut import M4_NUT, MetricNut, apply_hex_nut_tool


class TSlotProfile(NamedTuple):
    slot_width: float
    track_width: float
    track_depth: float
    neck_depth: float
    arm_thickness: float


PROFILE_4545 = TSlotProfile(
    slot_width=10.0,
    track_width=20.0,
    track_depth=6.0,
    neck_depth=6.0,
    arm_thickness=3.0,
)


def build_tslot_nut(
    profile: TSlotProfile = PROFILE_4545,
    nut: MetricNut = M4_NUT,
    length: float = 25.0,
    clearance: float = 0.2,
    interference: float = 0.2,
    nut_depth_past_neck: float = 2.0,
    screw_entry_chamfer=0.5,
) -> cq.Workplane:
    # Calculate dimensions with clearance
    slot_w = profile.slot_width - clearance
    track_w = profile.track_width - clearance
    neck_d = profile.neck_depth - clearance
    flange_d = nut_depth_past_neck + nut.thickness

    # Chamfer dimensions for the flange back corners
    chamfer_x = profile.arm_thickness
    chamfer_y = min(profile.arm_thickness, flange_d - 0.1)

    back_w = track_w - 2 * chamfer_x
    if back_w < slot_w:
        back_w = slot_w
        chamfer_x = (track_w - back_w) / 2

    # Build half the 2D profile in XY plane, then mirror
    half_profile = (
        cq.Workplane("XY")
        .polyline(
            [
                # Centerline at X=0
                (0, 0),
                # Right side of neck
                (slot_w / 2, 0),
                (slot_w / 2, neck_d),
                # Right side of flange
                (track_w / 2, neck_d),
                (track_w / 2, neck_d + flange_d - chamfer_y),
                (back_w / 2, neck_d + flange_d),
                # Back to centerline
                (0, neck_d + flange_d),
            ]
        )
        .close()
        .mirror(mirrorPlane="YZ")
        .extrude(length)
    )

    # Add hex nut cutout at Y=0 face, halfway up in Z
    wp_y0 = half_profile.faces("<Y").workplane()
    nut_locs = [(0, length / 2)]

    body = apply_hex_nut_tool(
        wp=wp_y0,
        locations=nut_locs,
        nut=nut,
        depth=neck_d + nut_depth_past_neck,
        angle=30.0,
        chamfer=screw_entry_chamfer,
    )

    return body


if __name__ == "__main__":
    cq.exporters.export(build_tslot_nut(), "tslot_nut.stl")

import math
import cadquery as cq
from typing import NamedTuple

from hardware_metric_nut import M4_NUT, MetricNut, apply_hex_nut_tool


class TSlotProfile(NamedTuple):
    """Defines the dimensions of a T-slot extrusion profile.

    Args:
        overall_width: Total width of the T-slot profile
        slot_width: Width of the narrow slot opening
        slot_depth: Depth of the narrow slot (neck) section
        track_width: Width of the wider track section
        track_depth: Total depth from outer edge to back of track (inclusive of slot_depth)
        arm_thickness: Diagonal thickness of the angled arm connecting slot to track
    """

    overall_width: float
    slot_width: float
    slot_depth: float
    track_width: float
    track_depth: float
    arm_thickness: float


PROFILE_4545 = TSlotProfile(
    overall_width=45.0,
    slot_width=10.0,
    slot_depth=6.0,
    track_width=20.0,
    track_depth=13.0,
    arm_thickness=3.0,
)


def build_tslot_nut(
    profile: TSlotProfile = PROFILE_4545,
    nut: MetricNut = M4_NUT,
    length: float = 25.0,
    clearance: float = 0.2,
    interference: float = 0.2,
    nut_depth_past_neck: float = 2.0,
    screw_entry_chamfer: float = 0.5,
) -> cq.Workplane:
    """Build a T-slot nut for mounting into T-slot extrusion profiles.

    The nut is designed to be 3D printed in a standing orientation (extruded along Z).
    The Y=0 plane represents the outer edge of the T-slot profile.

    Args:
        profile: T-slot profile dimensions
        nut: Metric hex nut specifications
        length: Length of the T-slot nut body (Z direction)
        clearance: Uniform clearance to subtract from profile dimensions for fit
        interference: Reserved for future spring feature implementation
        nut_depth_past_neck: How far past the slot neck the hex nut pocket extends
        screw_entry_chamfer: Chamfer size for screw entry hole

    Returns:
        CadQuery workplane with the T-slot nut body
    """
    # Calculate dimensions with clearance
    slot_w = profile.slot_width - clearance
    slot_d = profile.slot_depth + clearance
    flange_w = profile.track_width - clearance
    flange_d = nut_depth_past_neck + nut.thickness

    # Calculate the chamfer, the horizontal distance to inset the flange outer edges
    # The distance from the flange depth to the profile center is the same as the flange width to
    # the diagonal profile centerline
    flange_to_profile_center = (
        profile.overall_width / 2
        - profile.slot_depth
        - nut_depth_past_neck
        - nut.thickness
    )
    # subtract out the horizontal projection of the arm thickness in its quadrant to get the maximim width
    flange_max_w = flange_to_profile_center - (
        profile.arm_thickness / 2 + clearance
    ) * math.sqrt(2)
    # The chamfer is how much this cuts in from the track width
    chamfer = max(flange_w / 2 - flange_max_w, 0)

    # Build half the 2D profile in XY plane, then mirror
    half_profile = (
        cq.Workplane("XY")
        .polyline(
            [
                # Centerline at X=0
                (0, 0),
                # Right side of neck
                (slot_w / 2, 0),
                (slot_w / 2, slot_d),
                # Right side of flange
                (flange_w / 2, slot_d),
                (flange_w / 2, slot_d + flange_d - chamfer),
                (flange_w / 2 - chamfer, slot_d + flange_d),
                # Back to centerline
                (0, slot_d + flange_d),
            ]
        )
        .close()
        # .mirror(mirrorPlane="YZ")
        .extrude(length)
    )

    # Add hex nut cutout at Y=0 face, halfway up in Z
    wp_y0 = half_profile.faces("<Y").workplane()
    nut_locs = [(0, length / 2)]

    body = apply_hex_nut_tool(
        wp=wp_y0,
        locations=nut_locs,
        nut=nut,
        depth=slot_d + nut_depth_past_neck,
        angle=30.0,
        chamfer=screw_entry_chamfer,
    )

    return body


if __name__ == "__main__":
    cq.exporters.export(build_tslot_nut(), "tslot_nut.stl")

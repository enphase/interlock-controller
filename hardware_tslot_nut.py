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

    def track_bottom_halfwidth(self) -> float:
        slot_bottom_to_profile_center = self.overall_width / 2 - self.track_depth
        return slot_bottom_to_profile_center - (self.arm_thickness / 2) * math.sqrt(2)

    def chamfer(self) -> float:
        """Returns the horizontal distance to inset the flange outer edges."""
        return self.track_width / 2 - self.track_bottom_halfwidth()


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
    nut_depth_past_neck: float = 2.0,  # effectively wall thickness
    screw_entry_chamfer: float = 0.5,
    spring_thickness: float = 2.0,
    spring_height: float = 6.0,
    spring_interference: float = 1.0,
) -> cq.Workplane:
    """Build a T-slot nut for mounting into T-slot extrusion profiles.

    The nut is designed to be 3D printed in a standing orientation (extruded along Z).
    The Y=0 plane represents the outer edge of the T-slot profile.

    Args:
        profile: T-slot profile dimensions
        nut: Metric hex nut specifications
        length: Length of the T-slot nut body (Z direction)
        clearance: Uniform clearance to subtract from profile dimensions for fit
        nut_depth_past_neck: How far past the slot neck the hex nut pocket extends
        screw_entry_chamfer: Chamfer size for screw entry hole

    Returns:
        CadQuery workplane with the T-slot nut body
    """
    # Calculate dimensions with clearance
    neck_w = profile.slot_width - clearance * 2
    flange_w = profile.track_width - clearance * 2
    flange_y_start = profile.slot_depth  # y-coord at which flange starts
    flange_d = nut_depth_past_neck + nut.thickness
    flange_y_end = flange_y_start + flange_d

    # at max depth, inset by diagonal clearance
    chamfer = profile.chamfer() + clearance * math.sqrt(2)
    flange_chamfer = max(
        chamfer - (profile.track_depth - profile.slot_depth - flange_d), 0
    )

    # Build half the 2D profile in XY plane, then mirror
    body = (
        cq.Workplane("XY")
        .polyline(
            [
                # Centerline at X=0
                (0, 0),
                # Right side of neck
                (neck_w / 2, 0),
                (neck_w / 2, flange_y_start),
                # Right side of flange
                (flange_w / 2, flange_y_start),
                (flange_w / 2, flange_y_end - flange_chamfer),
                (flange_w / 2 - flange_chamfer, flange_y_end),
                # Back to centerline
                (0, flange_y_end),
            ]
        )
        .close()
        .extrude(length)
        .mirror(mirrorPlane="YZ", union=True)
    )

    # Add hex nut cutout at Y=0 face, halfway up in Z
    nut_locs = [(0, length / 2)]
    body = apply_hex_nut_tool(
        wp=body.faces("<Y").workplane(),
        locations=nut_locs,
        nut=nut,
        depth=profile.slot_depth + nut_depth_past_neck,
        angle=30.0,
        chamfer=screw_entry_chamfer,
    )

    spring_y_end = profile.track_depth - clearance
    spring_y_start = profile.track_depth - clearance - spring_thickness
    spring_chamfer = chamfer - clearance  # account for truncated bottom from clearance

    spring_recess = (
        cq.Workplane("XY")
        .polyline(
            [
                (-spring_height / 2 - clearance * 2, spring_y_end),
                (spring_height / 2 + spring_thickness, spring_y_end),
                (
                    spring_height / 2 + spring_thickness,
                    spring_y_end - spring_thickness * 2 - clearance * 2,
                ),
                (
                    -spring_height / 2 - clearance * 2,
                    spring_y_end - spring_thickness * 2 - clearance * 2,
                ),
            ]
        )
        .close()
        .extrude(spring_height + clearance * 2)
    )
    body = body.cut(spring_recess)

    spring_base = (
        cq.Workplane("XY")
        .polyline(
            [
                # Start at the edge of the spring
                (spring_height / 2 + spring_thickness, flange_y_start),
                # Right side of flange
                (flange_w / 2, flange_y_start),
                (flange_w / 2, spring_y_end - spring_chamfer),
                (flange_w / 2 - spring_chamfer, spring_y_end),
                # Back to start
                (spring_height / 2 + spring_thickness, spring_y_end),
            ]
        )
        .close()
        .extrude(spring_height)
    )
    body = body.union(spring_base)

    spring_arm = (
        cq.Workplane("XY")
        .polyline(
            [
                (spring_height / 2 + spring_thickness, spring_y_start),
                (-spring_height / 2, spring_y_start),
                (-spring_height / 2, spring_y_end),
                (spring_height / 2 + spring_thickness, spring_y_end),
            ]
        )
        .close()
        .extrude(spring_height)
    )
    body = body.union(spring_arm)

    return body


if __name__ == "__main__":
    cq.exporters.export(build_tslot_nut(), "tslot_nut.stl")

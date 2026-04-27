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


# from https://www.onlinemetals.com/en/buy/aluminum/45mm-x-45mm-light-w-10mm-slot-aluminum-t-slot-6063/pid/mp-00001401
PROFILE_4545 = TSlotProfile(
    overall_width=45.0,
    slot_width=10.0,
    slot_depth=6.0,
    track_width=20.1,
    track_depth=14.5,
    arm_thickness=3.0,
)


def shapely_to_cq(poly):
    """Convert a Shapely polygon or multipolygon to a list of CadQuery Faces."""
    if poly.geom_type == "Polygon":
        polygons = [poly]
    elif poly.geom_type == "MultiPolygon":
        polygons = poly.geoms
    else:
        return []

    faces = []
    for p in polygons:
        ext_points = list(p.exterior.coords)
        ext_wire = cq.Workplane("XY").polyline(ext_points).close().wire().val()

        int_wires = []
        for interior in p.interiors:
            int_points = list(interior.coords)
            int_wires.append(
                cq.Workplane("XY").polyline(int_points).close().wire().val()
            )

        face = cq.Face.makeFromWires(ext_wire, int_wires)
        faces.append(face)

    return faces


def build_tslot_nut(
    profile: TSlotProfile = PROFILE_4545,
    nut: MetricNut = M4_NUT,
    clearance: float = 0.2,
    wall: float = 2.0,
    screw_entry_chamfer: float = 0.5,
    spring_thickness: float = 2.0,
    spring_height: float = 4.0,
    spring_interference: float = 1.0,
) -> cq.Workplane:
    """Build a T-slot nut for mounting into T-slot extrusion profiles.

    The nut is designed to be 3D printed in a standing orientation (extruded along Z).
    The Y=0 plane represents the outer edge of the T-slot profile.

    Height is automatically calculated.

    Args:
        profile: T-slot profile dimensions
        nut: Metric hex nut specifications
        clearance: Uniform clearance to subtract from profile dimensions for fit
        wall: Wall thickness, including for the distance from the flange to the nut pocket
        screw_entry_chamfer: Chamfer size for screw entry hole

    Returns:
        CadQuery workplane with the T-slot nut body
    """
    from shapely.geometry import Polygon, box

    nut_center_z = (
        spring_height + clearance * 2 + wall + nut.across_flats / 2 * math.sqrt(3) / 2
    )
    height = nut_center_z + nut.across_flats / 2 * math.sqrt(3) / 2 + wall

    # 1. Define outer exact boundaries of the track
    track_nominal = Polygon(
        [
            (-profile.track_width / 2, profile.slot_depth),
            (profile.track_width / 2, profile.slot_depth),
            (profile.track_width / 2, profile.track_depth - profile.chamfer()),
            (profile.track_width / 2 - profile.chamfer(), profile.track_depth),
            (-profile.track_width / 2 + profile.chamfer(), profile.track_depth),
            (-profile.track_width / 2, profile.track_depth - profile.chamfer()),
        ]
    )
    neck_nominal = box(
        -profile.slot_width / 2,
        0.0,
        profile.slot_width / 2,
        profile.slot_depth,
    )

    flange_y_end = profile.slot_depth + wall + nut.thickness
    flange_nominal = track_nominal & box(
        -profile.track_width / 2,
        clearance * 2,  # starts offset to ensure flange clamps before neck bottoms out
        profile.track_width / 2,
        flange_y_end,
    )
    base_nominal = neck_nominal | flange_nominal
    base_actual = base_nominal.buffer(-clearance, join_style="bevel")

    # 3. Spring Arm Nominal
    # Construct spring arm by shelling the track, then restricting to the bounding box
    track_cleared = track_nominal.buffer(-clearance, join_style="bevel")
    spring_shell = track_cleared - track_cleared.buffer(
        -spring_thickness, join_style="bevel"
    )
    spring_arm = spring_shell & box(
        -spring_height / 2 - clearance * 2,
        profile.slot_depth,
        profile.track_width / 2,
        profile.track_depth,
    )

    # 4. Spring Recess
    # allow a gap of 1.5x spring interference for spring deflection
    recess_y_start = (
        profile.track_depth - spring_thickness - spring_interference * 1.5 - clearance
    )
    recess_cut = box(
        -spring_height / 2 - clearance * 2,
        recess_y_start,
        profile.track_width / 2,
        profile.track_depth,
    )

    # Compile layers
    spring_actual = (base_actual - recess_cut) | spring_arm
    # spring_actual = base_actual - recess_cut

    # 6. Convert to CadQuery and extrude
    body = cq.Workplane("XY").add(shapely_to_cq(spring_actual)).extrude(spring_height)
    body = body.union(
        cq.Workplane("XY")
        .add(shapely_to_cq(base_actual))
        .extrude(height - spring_height)
        .translate((0, 0, spring_height))
    )

    # 7. Apply Hex Nut Cutout
    nut_locs = [(0, nut_center_z)]
    body = apply_hex_nut_tool(
        wp=body.faces("<Y").workplane(),
        locations=nut_locs,
        nut=nut,
        depth=profile.slot_depth + wall,
        angle=30.0,
        chamfer=screw_entry_chamfer,
    )

    # 8. Interference Nub
    # Nub is centered at X=0, attaches to the tip of the spring arm
    actual_spring_y_end = spring_actual.bounds[3]
    h = spring_height / 2
    l = spring_interference
    chord_length = math.sqrt(l**2 + h**2)
    arc_radius = (h**2 + l**2) / (2 * l)
    sagitta = arc_radius - math.sqrt(arc_radius**2 - (chord_length / 2) ** 2)
    nub_center_z = spring_height / 2

    interference_nub = (
        cq.Workplane("YZ")
        .moveTo(actual_spring_y_end, 0)
        .sagittaArc(
            (actual_spring_y_end + spring_interference, spring_height / 2), -sagitta
        )
        .lineTo(actual_spring_y_end, spring_height / 2)
        .close()
        .revolve(360, (0, nub_center_z), (1, nub_center_z))
    )
    body = body.union(interference_nub)

    return body


if __name__ == "__main__":
    cq.exporters.export(build_tslot_nut(), "tslot_nut.stl")

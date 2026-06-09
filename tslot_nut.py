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

import math
from pathlib import Path

import cadquery as cq
from typing import NamedTuple

from cad_lib.fasteners import M4_NUT, MetricNut, cut_hex_nut_pocket


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

    def inner_profile_polygon(self):
        """Returns a Shapely polygon of the full T-slot interior including neck.

        Coordinates: X centered on slot, Y=0 is the outer face of the profile, increasing inward.
        The polygon covers the neck (y ∈ [0, slot_depth]) and the track
        (y ∈ [slot_depth, track_depth]) with chamfered back corners.
        """
        from shapely.geometry import Polygon, box

        hw = self.track_width / 2
        c = self.chamfer()
        track = Polygon(
            [
                (-hw, self.slot_depth),
                (hw, self.slot_depth),
                (hw, self.track_depth - c),
                (hw - c, self.track_depth),
                (-hw + c, self.track_depth),
                (-hw, self.track_depth - c),
            ]
        )
        neck = box(-self.slot_width / 2, 0, self.slot_width / 2, self.slot_depth)
        return track | neck


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
    from shapely.geometry import box

    nut_center_z = (
        spring_height
        + clearance * 2
        + wall
        + nut.nut_hex_across_flats / 2 * math.sqrt(3) / 2
    )
    height = nut_center_z + nut.nut_hex_across_flats / 2 * math.sqrt(3) / 2 + wall

    # clamp in -Y so neck is upper third of slot, allowing a neck on the other side of the slot
    # clamp in +Y to provide room for the spring
    flange_y_end = profile.slot_depth + wall + nut.nut_thickness
    base_nominal = profile.inner_profile_polygon() & box(
        -profile.track_width / 2,
        profile.slot_depth * (2 / 3),
        profile.track_width / 2,
        flange_y_end,
    )
    base_actual = base_nominal.buffer(-clearance, join_style="bevel")

    # 3. Spring Arm Nominal
    # Construct spring arm by shelling the track, then restricting to the bounding box
    track_cleared = profile.inner_profile_polygon().buffer(
        -clearance, join_style="bevel"
    )
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

    # Create body first
    body = (
        cq.Workplane("XY")
        .add(shapely_to_cq(base_actual))
        .extrude(height - spring_height)
        .translate((0, 0, spring_height))
    )

    # Apply hex pocket while +Y is the right face
    nut_locs = [(0, nut_center_z)]
    body = cut_hex_nut_pocket(
        wp=body.faces(">Y").workplane(),
        locations=nut_locs,
        nut=nut,
        angle=30.0,
        chamfer=screw_entry_chamfer,
    )

    # Add spring arm
    body = body.union(
        cq.Workplane("XY").add(shapely_to_cq(spring_actual)).extrude(spring_height)
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
    Path("generated").mkdir(parents=True, exist_ok=True)
    cq.exporters.export(build_tslot_nut(), "generated/tslot_nut_4545_m4.stl")

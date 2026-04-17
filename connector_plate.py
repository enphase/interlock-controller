import cadquery as cq

from hardware_719w import apply_719w_cutouts
from hardware_m12 import apply_m12_cutouts
from hardware_metric_nut import M3_NUT, apply_hex_nut_tool

# --- Parameters ---

# Note on Coordinate System:
# The box is centered at the origin (X, Y).
# Z=0 is the printbed (bottom face of the print) AND the external face of the plate.
# +Z goes up and represents going into the enclosure.
# The plate occupies Z=[0, plate_thickness].

# Plate dimensions
FLANGE_MARGIN = 4.0

# Hex nut flanges
HEX_NUT = M3_NUT
NUT_DEPTH = 1.5
HEX_FLANGE_RADIUS = 4.0

M12_CONNECTOR_SPACING = 25.0

# Emboss Parameters (Extruded upwards from the inside face)
EMBOSS_THICKNESS = 0.4
EMBOSS_WIDTH = 1.0


def make_d_flange_sketch(radius: float, extension: float, dir_x: float) -> cq.Sketch:
    """
    Creates a reusable 2D sketch for a D-shaped flange.
    It is a round rect on the outside (180 degrees) and a square/rect on the inside.
    dir_x: 1 points right (+x), -1 points left (-x)
    """
    return (
        cq.Sketch()
        .circle(radius)
        .push([(-dir_x * extension / 2, 0)])
        .rect(extension, radius * 2)
    )


def build_base_plate(
    length: float,
    width: float,
    cutout_radius: float,
    thickness: float = 2.5,
    *,
    screw_pattern_length_offset: float = 0.0,
    screw_pattern_width_offset: float = 0.0,
    add_cutout_emboss: bool = True,
    version_text: str = "",
) -> cq.Workplane:
    """
    Builds the base plate with screw flanges and optional cutout outline emboss.
    """
    # 1. Create the main plate
    plate = (
        cq.Workplane("XY")
        .rect(length + 2 * FLANGE_MARGIN, width + 2 * FLANGE_MARGIN)
        .extrude(thickness)
        .edges("|Z")
        .fillet(cutout_radius + FLANGE_MARGIN)
    )

    # 2. Add D-flanges for the hex nuts
    screw_pattern_length = length + screw_pattern_length_offset * 2
    screw_pattern_width = width + screw_pattern_width_offset * 2
    screw_locations = [
        (screw_pattern_length / 2, screw_pattern_width / 2),
        (screw_pattern_length / 2, -screw_pattern_width / 2),
        (-screw_pattern_length / 2, screw_pattern_width / 2),
        (-screw_pattern_length / 2, -screw_pattern_width / 2),
    ]
    hex_flange_radius = HEX_FLANGE_RADIUS
    for loc in screw_locations:
        dir_x = 1 if loc[0] > 0 else -1
        # Extension ensures it deeply overlaps into the main plate for unioning
        sketch = make_d_flange_sketch(hex_flange_radius, cutout_radius, dir_x)
        flange_wp = (
            cq.Workplane("XY")
            .center(loc[0], loc[1])
            .placeSketch(sketch)
            .extrude(thickness)
        )
        plate = plate.union(flange_wp)

    # 3. Cut the hex nut slots and clearance holes using the tool modifier
    # We start from the bottom face (<Z) to pocket the nut upward, then cut clearance through all
    plate = apply_hex_nut_tool(
        plate.faces("<Z"),
        screw_locations,
        HEX_NUT,
        depth=NUT_DEPTH,
        chamfer=0.5,
    )

    # 4. Add Cutout Outline Emboss
    if add_cutout_emboss:
        outer_w = length + EMBOSS_WIDTH
        outer_h = width + EMBOSS_WIDTH
        outer_r = cutout_radius + EMBOSS_WIDTH / 2

        inner_w = length - EMBOSS_WIDTH
        inner_h = width - EMBOSS_WIDTH
        inner_r = cutout_radius - EMBOSS_WIDTH / 2

        cutout_emboss_base = (
            cq.Workplane("XY")
            .workplane(offset=thickness)
            .rect(outer_w, outer_h)
            .extrude(EMBOSS_THICKNESS)
            .edges("|Z")
            .fillet(outer_r)
        )

        cutout_emboss_hole = (
            cq.Workplane("XY")
            .workplane(
                offset=thickness - 0.1
            )  # Offset lower to avoid coincident face issues
            .rect(inner_w, inner_h)
            .extrude(EMBOSS_THICKNESS + 0.2)
            .edges("|Z")
            .fillet(inner_r)
        )

        cutout_emboss = cutout_emboss_base.cut(cutout_emboss_hole)
        plate = plate.union(cutout_emboss)

    # 5. Version Text Emboss
    if version_text:
        text_x = length / 2 - FLANGE_MARGIN - cutout_radius
        text_y = -width / 2 + FLANGE_MARGIN

        text_emboss = (
            cq.Workplane("XY")
            .workplane(offset=thickness)
            .center(text_x, text_y)
            .text(
                version_text,
                fontsize=4.0,
                distance=EMBOSS_THICKNESS,
                halign="right",
                valign="bottom",
            )
        )
        plate = plate.union(text_emboss)

    return plate


def build_bottom_cutout_plate() -> cq.Workplane:
    cutout_length = 116.0
    cutout_width = 40.0
    cutout_radius = 12.7  # 0.5 inches

    # M12 Connectors
    num_connectors = 2

    connector_locations = [
        (cutout_length / 2 - M12_CONNECTOR_SPACING * (i + 0.5), 0)
        for i in range(num_connectors)
    ]

    # AC Power Entry Module
    power_locations = [(-cutout_length / 2 + 25.0, 0)]

    plate = build_base_plate(
        length=cutout_length,
        width=cutout_width,
        cutout_radius=cutout_radius,
        add_cutout_emboss=True,
        version_text="BOT v1.0",
    )

    # 5. Cut the M12 connector holes using the reusable sketch profile
    # We start from the bottom face (<Z) and cut through all downwards
    # In order to place the chamfer on the exterior face (Z=0), we pass in the bottom face
    plate = apply_m12_cutouts(plate.faces("<Z").workplane(), connector_locations)

    # 6. Cut the 719W AC Power Entry Module cutout
    plate = apply_719w_cutouts(
        plate.faces("<Z"),
        power_locations,
        HEX_NUT,
        depth=NUT_DEPTH,
        chamfer=0.5,
    )

    return plate


def build_top_cutout_plate() -> cq.Workplane:
    cutout_length = 116.0
    cutout_width = 40.0
    cutout_radius = 12.7  # 0.5 inches

    # M12 Connectors
    num_connectors = 4

    connector_locations = [
        (M12_CONNECTOR_SPACING * ((num_connectors / 2) - i - 0.5), 0)
        for i in range(num_connectors)
    ]

    # 5. Cut the M12 connector holes using the reusable sketch profile
    # We start from the bottom face (<Z) and cut through all downwards
    # In order to place the chamfer on the exterior face (Z=0), we pass in the bottom face
    plate = build_base_plate(
        length=cutout_length,
        width=cutout_width,
        cutout_radius=cutout_radius,
        add_cutout_emboss=True,
        version_text="TOP v1.0",
    )

    plate = apply_m12_cutouts(plate.faces("<Z").workplane(), connector_locations)

    return plate


def build_side_cutout_plate() -> cq.Workplane:
    cutout_length = 216.0
    cutout_width = 40.0
    cutout_radius = 12.7  # 0.5 inches

    # M12 Connectors
    connector_locations = [(-cutout_length / 2 + M12_CONNECTOR_SPACING * 1.5, 0)]

    # 5. Cut the M12 connector holes using the reusable sketch profile
    # We start from the bottom face (<Z) and cut through all downwards
    # In order to place the chamfer on the exterior face (Z=0), we pass in the bottom face
    plate = build_base_plate(
        length=cutout_length,
        width=cutout_width,
        cutout_radius=cutout_radius,
        add_cutout_emboss=True,
        version_text="SIDE v1.0",
    )

    plate = apply_m12_cutouts(plate.faces("<Z").workplane(), connector_locations)

    return plate


# --- Export ---
if __name__ == "__main__":
    print("Exporting...")
    cq.exporters.export(build_top_cutout_plate(), "top_plate.stl")
    cq.exporters.export(build_bottom_cutout_plate(), "bot_plate.stl")
    cq.exporters.export(build_side_cutout_plate(), "side_plate.stl")
    print("Done!")

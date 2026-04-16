import cadquery as cq
from typing import List, Tuple

from hardware_metric_nut import MetricNut, M3_NUT, apply_hex_nut_tool
from hardware_m12 import apply_m12_cutouts

# --- Parameters ---

# Note on Coordinate System:
# The box is centered at the origin (X, Y).
# Z=0 is the printbed (bottom face of the print) AND the external face of the plate.
# +Z goes up and represents going into the enclosure.
# The plate occupies Z=[0, plate_thickness].

# Plate dimensions
cutout_length = 216.0
cutout_width = 40.0
cutout_radius = 12.7 # 0.5 inches
flange_margin = 5.0  

main_plate_length = cutout_length + 2 * flange_margin
main_plate_width = cutout_width + 2 * flange_margin
plate_thickness = 4.0
edge_radius = cutout_radius + flange_margin # External corners

# Hex nut flanges
hex_flange_margin = 3.5 
hex_flange_radius = (M3_NUT.across_flats / 0.866025) / 2 + hex_flange_margin

# Emboss Parameters (Extruded upwards from the inside face)
emboss_thickness = 0.4
emboss_width = 1.0
m12_emboss_dia = 18.0
version_text = "v1.0"

# M12 Connectors
num_connectors = 4

connector_spacing = cutout_length / (num_connectors + 1)
connector_locations = [
    (connector_spacing * (i + 1) - cutout_length / 2, 0)
    for i in range(num_connectors)
]

# Screws and Hex Nuts
screw_pattern_length = 228.0
screw_pattern_width = 24.0
m3_nut_depth = M3_NUT.thickness + 0.2 

screw_locations = [
    (screw_pattern_length / 2, screw_pattern_width / 2),
    (screw_pattern_length / 2, -screw_pattern_width / 2),
    (-screw_pattern_length / 2, screw_pattern_width / 2),
    (-screw_pattern_length / 2, -screw_pattern_width / 2)
]

# --- Tool Profiles & Modifiers ---

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

# --- Build the CAD Model ---

# 1. Create the main plate
plate = (
    cq.Workplane("XY")
    .rect(main_plate_length, main_plate_width)
    .extrude(plate_thickness)
    .edges("|Z")
    .fillet(edge_radius)
)

# 2. Add D-flanges for the hex nuts
for loc in screw_locations:
    dir_x = 1 if loc[0] > 0 else -1
    # Extension ensures it deeply overlaps into the main plate for unioning
    sketch = make_d_flange_sketch(hex_flange_radius, hex_flange_radius + flange_margin, dir_x)
    flange_wp = (
        cq.Workplane("XY")
        .center(loc[0], loc[1])
        .placeSketch(sketch)
        .extrude(plate_thickness)
    )
    plate = plate.union(flange_wp)

# 3. Cut the M12 connector holes using the reusable sketch profile
# We start from the top face (>Z) and cut through all downwards
plate = apply_m12_cutouts(
    plate.faces(">Z").workplane(), 
    connector_locations
)

# Add 1mm 45-degree chamfer to the M12 holes on the external face (Z=0)
for loc in connector_locations:
    x, y = loc
    box = cq.selectors.BoxSelector((x - 10, y - 10, -0.1), (x + 10, y + 10, 0.1))
    plate = plate.faces("<Z").edges(box).chamfer(1.0)

# 4. Cut the M3 hex nut slots and clearance holes using the tool modifier
# We start from the top face (>Z) to pocket downwards, then cut clearance through all
plate = apply_hex_nut_tool(
    plate.faces(">Z").workplane(),
    screw_locations,
    M3_NUT,
    m3_nut_depth
)

# 5. Add Embosses
# 5a. Cutout Outline Emboss
outer_w = cutout_length + emboss_width
outer_h = cutout_width + emboss_width
outer_r = cutout_radius + emboss_width/2

inner_w = cutout_length - emboss_width
inner_h = cutout_width - emboss_width
inner_r = cutout_radius - emboss_width/2

cutout_emboss_base = (
    cq.Workplane("XY")
    .workplane(offset=plate_thickness)
    .rect(outer_w, outer_h)
    .extrude(emboss_thickness)
    .edges("|Z")
    .fillet(outer_r)
)

cutout_emboss_hole = (
    cq.Workplane("XY")
    .workplane(offset=plate_thickness - 0.1) # Offset lower to avoid coincident face issues
    .rect(inner_w, inner_h)
    .extrude(emboss_thickness + 0.2)
    .edges("|Z")
    .fillet(inner_r)
)

cutout_emboss = cutout_emboss_base.cut(cutout_emboss_hole)
plate = plate.union(cutout_emboss)

# 5b. M12 Circular Emboss
m12_outer_dia = m12_emboss_dia + emboss_width
m12_inner_dia = m12_emboss_dia - emboss_width

m12_emboss_sketch = (
    cq.Sketch()
    .circle(m12_outer_dia / 2)
    .circle(m12_inner_dia / 2, mode='s')
)

m12_emboss = (
    cq.Workplane("XY")
    .workplane(offset=plate_thickness)
    .pushPoints(connector_locations)
    .placeSketch(m12_emboss_sketch)
    .extrude(emboss_thickness)
)
plate = plate.union(m12_emboss)

# 5c. Version Text Emboss
text_x = main_plate_length / 2 - 2.0
text_y = -main_plate_width / 2 + 1.5

text_emboss = (
    cq.Workplane("XY")
    .workplane(offset=plate_thickness)
    .center(text_x, text_y)
    .text(version_text, fontsize=4.0, distance=emboss_thickness, halign="right", valign="bottom")
)
plate = plate.union(text_emboss)


# --- Export ---
if __name__ == "__main__":
    print("Exporting...")
    cq.exporters.export(plate, "connector_plate.stl")
    cq.exporters.export(plate, "connector_plate.step")
    print("Done!")

import cadquery as cq
from typing import List, Tuple

PANEL_CUTOUT_DIA = 15.4
PANEL_CUTOUT_FLATS = 13.5


def apply_m12_cutouts(
    wp: cq.Workplane, locations: List[Tuple[float, float]], *, tol: float = 0.2
) -> cq.Workplane:
    """
    Applies the M12 double-D cutouts to the given workplane, cutting through all.
    Specified for T4171210004-001 (standard PG9 double-D cutout).
    """
    sketch = (
        cq.Sketch()
        .circle(PANEL_CUTOUT_DIA / 2 + tol)
        .rect(PANEL_CUTOUT_FLATS + tol * 2, PANEL_CUTOUT_DIA + tol * 2, mode="i")
    )

    # Create a 1mm 45-degree chamfer by cutting a tapered hole from 1mm inside the face, expanding outwards
    res = (
        wp.workplane(offset=-1.0)
        .pushPoints(locations)
        .placeSketch(sketch)
        .cutBlind(1.0, taper=-45)
    )
    res = res.pushPoints(locations).placeSketch(sketch).cutThruAll()

    return res

import cadquery as cq
from typing import List, Tuple

PANEL_CUTOUT_DIA = 15.4
PANEL_CUTOUT_FLATS = 13.5


def cut_m12_connector_holes(
    wp: cq.Workplane, locations: List[Tuple[float, float]], *, tol: float = 0.0
) -> cq.Workplane:
    """
    Cuts M12 double-D connector holes into the workplane, cutting through all.
    Specified for T4171210004-001 (standard PG9 double-D cutout).

    It is assumed the cutout pattern is pre-toleranced.
    """
    sketch = (
        cq.Sketch()
        .circle(PANEL_CUTOUT_DIA / 2 + tol)
        .rect(PANEL_CUTOUT_FLATS + tol * 2, PANEL_CUTOUT_DIA + tol * 2, mode="i")
    )

    res = wp

    # Create a 1mm 45-degree chamfer by cutting a tapered hole from 1mm inside the face, expanding outwards
    res = (
        res.copyWorkplane(wp)
        .pushPoints(locations)
        .circle(PANEL_CUTOUT_DIA / 2 + tol + 2)
        .cutBlind(-2.0, taper=45)
    )

    res = res.copyWorkplane(wp).pushPoints(locations).placeSketch(sketch).cutThruAll()

    return res

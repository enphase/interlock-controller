import cadquery as cq
from typing import List, Tuple

def apply_m12_cutouts(
    wp: cq.Workplane, 
    locations: List[Tuple[float, float]],
    tol_dia: float = 0.1,
    tol_flats: float = 0.1
) -> cq.Workplane:
    """
    Applies the M12 double-D cutouts to the given workplane, cutting through all.
    Specified for T4171210004-001 (standard PG9 double-D cutout).
    """
    nom_dia = 15.4
    nom_flats_width = 13.5
    
    dia = nom_dia + tol_dia
    flats_width = nom_flats_width + tol_flats
    
    sketch = (cq.Sketch()
        .circle(dia / 2)
        .rect(flats_width, dia + 2, mode='i'))
    return wp.pushPoints(locations).placeSketch(sketch).cutThruAll()

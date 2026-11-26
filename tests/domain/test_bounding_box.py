from domain.value_objects.bounding_box import BoundingBox

def test_area_calculation():
    bbox = BoundingBox(x1=0, y1=0, x2=10, y2=10)
    assert bbox.area() == 100.0

def test_overlap_ratio():
    # Fruta: ocupa del 0 al 10 en X e Y
    fruta = BoundingBox(x1=0, y1=0, x2=10, y2=10)
    # Ave: está a la mitad de la fruta (del 5 al 10)
    ave = BoundingBox(x1=5, y1=5, x2=10, y2=10)
    
    # El área del ave es 25, y su intersección con la fruta es toda su área (25).
    # Por lo tanto, el 100% del ave está sobre la fruta.
    assert ave.overlap_ratio(fruta) == 1.0

def test_no_overlap():
    fruta = BoundingBox(x1=0, y1=0, x2=10, y2=10)
    ave = BoundingBox(x1=20, y1=20, x2=30, y2=30)
    
    assert ave.overlap_ratio(fruta) == 0.0

from domain.models.detection import Detection, DomainType
from domain.value_objects.bounding_box import BoundingBox
from domain.services.risk_analyzer import RiskAnalyzer

def test_ataque_de_loro_a_manzana():
    # Manzana mide 50px. Loro DEBE ser más grande (190px) para estar en el mismo plano (Z-ratio válido)
    fruta = Detection("apple", 0.9, BoundingBox(50, 50, 100, 100), DomainType.FRUIT)
    loro = Detection("parrot", 0.85, BoundingBox(10, 10, 200, 200), DomainType.BIRD)
    
    events = RiskAnalyzer.analyze_frame([fruta, loro])
    assert len(events) == 1
    assert events[0].bird.class_name == "parrot"
    assert events[0].fruit.class_name == "apple"

def test_tangara_cerca_de_manzana_es_ignorada():
    fruta = Detection("apple", 0.9, BoundingBox(50, 50, 100, 100), DomainType.FRUIT)
    # La matriz dice que la tangara no ataca manzanas
    tangara = Detection("tanager", 0.8, BoundingBox(40, 40, 140, 140), DomainType.BIRD)
    
    events = RiskAnalyzer.analyze_frame([fruta, tangara])
    assert len(events) == 0

def test_ave_cerca_pero_no_suficiente_superposicion():
    fruta = Detection("apple", 0.9, BoundingBox(50, 50, 100, 100), DomainType.FRUIT)
    # Loro con Z-ratio válido pero muy alejado (lejos del radio de peligro)
    loro = Detection("parrot", 0.85, BoundingBox(250, 250, 440, 440), DomainType.BIRD)
    
    events = RiskAnalyzer.analyze_frame([fruta, loro])
    assert len(events) == 0

def test_multiples_aves_y_frutas():
    manzana = Detection("apple", 0.9, BoundingBox(10, 10, 60, 60), DomainType.FRUIT)
    uva = Detection("grape", 0.9, BoundingBox(300, 300, 400, 400), DomainType.FRUIT)
    
    loro = Detection("parrot", 0.8, BoundingBox(0, 0, 190, 190), DomainType.BIRD) 
    zorzal = Detection("thrush", 0.8, BoundingBox(200, 200, 866, 866), DomainType.BIRD) 
    
    events = RiskAnalyzer.analyze_frame([manzana, uva, loro, zorzal])
    assert len(events) == 2

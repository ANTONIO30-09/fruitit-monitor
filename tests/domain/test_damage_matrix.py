from domain.services.damage_matrix import DamageMatrix

def test_loro_ataca_manzana():
    assert DamageMatrix.is_dangerous("parrot", "apple") is True

def test_tangara_ataca_manzana():
    # La tangara NO ataca manzanas
    assert DamageMatrix.is_dangerous("tanager", "apple") is False

def test_loro_ataca_guayaba():
    assert DamageMatrix.is_dangerous("parrot", "guava") is True

def test_carpintero_ataca_pera():
    # El carpintero ataca peras (nuevo en la matriz)
    assert DamageMatrix.is_dangerous("woodpecker", "pear") is True

def test_gorrion_ataca_fresa():
    # El gorrión ataca fresas (nuevo en la matriz)
    assert DamageMatrix.is_dangerous("sparrow", "strawberry") is True

def test_zorzal_ataca_uva():
    # El zorzal ataca uvas (nuevo en la matriz)
    assert DamageMatrix.is_dangerous("thrush", "grape") is True

def test_alias_palta_a_aguacate():
    # Prueba de robustez: el modelo dice "palta" pero la matriz usa "avocado"
    assert DamageMatrix.is_dangerous("toucan", "palta") is True

def test_ave_desconocida():
    assert DamageMatrix.is_dangerous("penguin", "apple") is False

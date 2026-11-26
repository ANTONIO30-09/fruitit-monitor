from dataclasses import dataclass

@dataclass(frozen=True)
class FruitProfile:
    """Configuración para una fruta específica (ej. manzana)."""
    name: str
    overlap_threshold: float = 0.15  # 15% de superposición mínima para considerarse interacción
    # Podríamos añadir más reglas aquí en el futuro (ej. severidad de daño)

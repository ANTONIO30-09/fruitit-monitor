from typing import Dict, Set

class DamageMatrix:
    # Tamaños reales en metros (para calcular profundidad Z)
    _REAL_SIZE: Dict[str, float] = {
        "toucan": 0.40, "parrot": 0.30, "woodpecker": 0.25,
        "thrush": 0.20, "tanager": 0.18, "sparrow": 0.15, "bird": 0.15,
        "apple": 0.08, "orange": 0.09, "mandarin": 0.07, 
        "mango": 0.12, "avocado": 0.10, "banana": 0.15, 
        "grape": 0.03, "peach": 0.08, "fig": 0.06, "guava": 0.07
    }

    _DANGER_MAP: Dict[str, Set[str]] = {
        "parrot": {"orange", "mandarin", "mango", "guava", "avocado", "apple", "peach", "fig"},
        "woodpecker": {"apple", "pear", "peach", "plum", "grape", "orange"},
        "thrush": {"grape", "cherry", "strawberry", "blackberry", "blueberry", "fig", "peach", "tomato"},
        "tanager": {"banana", "papaya", "guava", "cherimoya", "passion_fruit", "fig"},
        "toucan": {"papaya", "banana", "avocado", "mango", "guava"},
        "sparrow": {"grape", "strawberry", "raspberry", "blackberry"},
        "bird": {"orange", "mandarin", "mango", "guava", "avocado", "apple", "peach", "fig", "pear", "plum", "grape", "cherry", "strawberry", "blackberry", "blueberry", "tomato", "banana", "papaya", "cherimoya", "passion_fruit", "raspberry"}
    }

    _BEAK_FACTOR: Dict[str, float] = {
        "toucan": 1.8, "woodpecker": 1.3, "parrot": 1.3,
        "thrush": 1.1, "tanager": 1.1, "sparrow": 1.1, "bird": 1.2
    }

    @classmethod
    def get_real_size(cls, class_name: str) -> float:
        return cls._REAL_SIZE.get(class_name.lower(), 0.10) # 10cm por defecto

    @classmethod
    def get_beak_factor(cls, bird_class: str) -> float:
        return cls._BEAK_FACTOR.get(bird_class.lower(), 1.0)

    @classmethod
    def is_dangerous(cls, bird_class: str, fruit_class: str) -> bool:
        bird_class = bird_class.lower().strip()
        fruit_class = fruit_class.lower().strip()
        if fruit_class in ["citrus", "tangerine"]: fruit_class = "mandarin"
        if fruit_class in ["palta"]: fruit_class = "avocado"
        if bird_class not in cls._DANGER_MAP: return False
        return fruit_class in cls._DANGER_MAP[bird_class]

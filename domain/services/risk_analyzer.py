from typing import List
from datetime import datetime
from zoneinfo import ZoneInfo
from domain.models.detection import Detection, DomainType
from domain.models.risk_event import RiskEvent
from domain.services.damage_matrix import DamageMatrix

class RiskAnalyzer:
    @staticmethod
    def analyze_frame(detections: List[Detection]) -> List[RiskEvent]:
        birds = [d for d in detections if d.domain_type == DomainType.BIRD]
        fruits = [d for d in detections if d.domain_type == DomainType.FRUIT]
        events = []
        
        for bird in birds:
            for fruit in fruits:
                if not DamageMatrix.is_dangerous(bird.class_name, fruit.class_name):
                    continue
                
                w_fruta_px = fruit.bbox.width()
                w_ave_px = bird.bbox.width()
                
                # Evitar división por cero si la caja es muy pequeña
                if w_ave_px < 1 or w_fruta_px < 1: continue

                # --- 1. CÁLCULO DE PROFUNDIDAD RELATIVA Z ---
                # Z_ave / Z_fruta = (W_real_ave / w_px_ave) / (W_real_fruta / w_px_fruta)
                w_real_ave = DamageMatrix.get_real_size(bird.class_name)
                w_real_fruta = DamageMatrix.get_real_size(fruit.class_name)
                
                z_ratio = (w_real_ave / w_ave_px) / (w_real_fruta / w_fruta_px)
                
                # Si el ave está en el fondo o muy al frente (fuera del plano), es falsa alarma.
                if not (0.01 <= z_ratio <= 20.0):
                    print(f"DEBUG Z -> Rechazado: {bird.class_name} en distinto plano (Z_ratio: {z_ratio:.2f})")
                    continue

                # --- 2. CÁLCULO DE PELIGRO (Si pasan el filtro Z) ---
                alpha_pico = DamageMatrix.get_beak_factor(bird.class_name)
                radio_peligro = (w_fruta_px / 2) + ((w_ave_px / 2) * alpha_pico)
                distancia = bird.bbox.distance_to(fruit.bbox)
                danger_score = radio_peligro / distancia
                
                print(f"DEBUG MATH -> {bird.class_name} | Z_ratio: {z_ratio:.2f} | Score: {danger_score:.2f}")
                
                if danger_score >= 1.0:
                    msg = f"¡PELIGRO ROJO! {bird.class_name.upper()} atacando {fruit.class_name.upper()}"
                elif danger_score >= 0.7:
                    msg = f"Pre-alerta: {bird.class_name.upper()} merodeando {fruit.class_name.upper()}"
                else:
                    continue
                
                events.append(RiskEvent(
                    bird=bird, fruit=fruit, timestamp=datetime.now(ZoneInfo("America/La_Paz")), 
                    message=msg, danger_score=danger_score
                ))
                    
        return events

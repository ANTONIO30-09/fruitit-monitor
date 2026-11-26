# 🦜 Fruitit Monitor - Protección Predictiva de Cultivos

Sistema de visión artificial en tiempo real para la protección predictiva de cultivos. Utiliza un modelo **YOLOv8 personalizado** para detectar aves y frutas, calcula matemáticamente el riesgo de picoteo mediante cinemática espacial, y muestra las alertas en un dashboard web premium con **Glassmorphism**.

## 🛠️ Stack Tecnológico
- **Backend**: Python 3.10+, FastAPI, SQLAlchemy (SQLite), WebSockets.
- **Frontend**: HTML5, CSS3 (Glassmorphism, diseño responsivo), JavaScript Vanilla.
- **Visión Artificial**: YOLOv8n (ONNX Runtime) entrenado con 6 clases personalizadas.
- **Data & Reportes**: Pandas, OpenPyXL (Exportación a Excel).
- **Hardware**: Integración con DroidCam (Cámara IP vía Wi-Fi).

## 🏗️ Arquitectura del Sistema (Hexagonal)
El proyecto sigue una Arquitectura Hexagonal (Ports & Adapters) para separar la lógica de negocio de las dependencias externas:

    .
    ├── api/                  # Adaptadores de entrada (FastAPI Routes, Auth, Schemas)
    ├── application/          # Casos de Uso (AnalyzeFrameUseCase)
    ├── domain/               # Núcleo puro (Modelos, Puertos, Value Objects, RiskAnalyzer)
    ├── infra/                # Adaptadores de salida (ONNX, SQLite, DroidCam, WebSockets)
    ├── frontend/             # Interfaz de usuario (HTML, CSS, JS, Video MP4)
    ├── models/               # Pesos del modelo entrenado (best.onnx)
    ├── tests/                # Suite de pruebas unitarias (PyTest)
    └── main.py               # Punto de entrada de FastAPI

## 🧠 Inteligencia Artificial (Modelo Personalizado)
No usamos un modelo genérico. Se entrenó un modelo **YOLOv8n** desde cero con un dataset de 140 imágenes (Roboflow) para detectar 6 clases específicas:
- **Aves**: parrot (Loro), toucan (Tucán), thrush (Zorzal).
- **Frutas**: mango, grape (Uva), avocado (Palta).

El modelo se exportó a **ONNX** para correr de forma ultra ligera en procesadores sin GPU (como un Intel Core i5).

## 📐 Lógica Matemática (Risk Analyzer)
El corazón del sistema es el RiskAnalyzer, que evalúa la probabilidad de daño usando:
1. **Filtro de Profundidad Relativa (Z-Ratio)**: Compara el tamaño real de la fruta vs. el tamaño en píxeles de la detección para descartar falsas alarmas (aves en el fondo).
2. **Matriz de Daño (DamageMatrix)**: Cruza la especie del ave con su fruta víctima. Si la combinación no es peligrosa biológicamente, se ignora.
3. **Cálculo de Peligro**: Score = Radio de Peligro / Distancia. Si el score es > 1.0 es ataque, si es > 0.7 es merodeo.

## ✨ Características Principales
- **Dashboard en Tiempo Real**: Actualización de alertas vía WebSockets sin recargar la página.
- **Glassmorphism UI**: Interfaz con efecto de vidrio esmerilado inspirado en iOS/VisionOS.
- **Control de Cámara**: Integración con DroidCam (IP configurable desde el frontend y botón de encendido/apagado).
- **Análisis Manual**: Subida de imágenes estáticas con vista previa.
- **Reportes**: Generación y descarga de historial de alertas en formato Excel (.xlsx).

## 🚀 Instalación y Uso

1. **Clonar el repositorio:**
    git clone https://github.com/ANTONIO30-09/fruitit-monitor.git
    cd fruitit-monitor

2. **Crear entorno virtual e instalar dependencias:**
    python -m venv .venv
    source .venv/bin/activate
    pip install -r requirements.txt

3. **Iniciar el servidor:**
    uvicorn main:app --reload

4. **Acceder al Dashboard:**
   Abre `http://localhost:8000` en tu navegador. Inicia sesión y conecta tu cámara DroidCam.

---
*Desarrollado por Antonio Vicente García Corrales para el Hito 5 de Minería de Datos (MDA-611).*

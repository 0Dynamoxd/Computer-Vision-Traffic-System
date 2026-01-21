#  Smart Traffic Control System (IoT + Computer Vision)

![Estado](https://img.shields.io/badge/Status-Finalizado-success)
![Python](https://img.shields.io/badge/Python-3.x-blue)
![Hardware](https://img.shields.io/badge/Hardware-ESP32S3%20%7C%20Arduino-red)
![Security](https://img.shields.io/badge/Security-HTTPS%20%7C%20TLS1.2-lock)

##  Descripción del Proyecto

Este proyecto consiste en un sistema autónomo de gestión de tráfico vehicular diseñado para optimizar el flujo en intersecciones urbanas. Utiliza **Visión Artificial (YOLOv8)** para detectar y contar vehículos en tiempo real y **Microcontroladores (ESP32)** para gestionar los semáforos.

El sistema fue validado en un **prototipo a escala (Maqueta)** utilizando vehículos tipo Hotwheels para simular escenarios de alta congestión, demostrando la viabilidad de la solución en un entorno controlado.



## Características Clave

* ** Visión Artificial:** Detección de vehículos en tiempo real usando el modelo **YOLOv8** personalizado.
* ** Lógica Inteligente:** El tiempo de los semáforos se ajusta dinámicamente según la cantidad de autos en espera (Algoritmo adaptativo).
* ** Ciberseguridad Robusta:**
    * **Nivel 1:** Acceso al dashboard protegido con Hashing (SHA-256).
* ** Dashboard de Control:** Interfaz gráfica desarrollada en **Streamlit** para monitoreo remoto y control manual/automático.
* ** Hardware Edge:** Procesamiento distribuido utilizando Seeed Studio XIAO ESP32S3.

##  Arquitectura de Hardware

* **Cámaras:** 4x Seeed Studio XIAO ESP32S3 Sense (Transmisión de video MJPEG sobre HTTPS).
* **Controlador de Semáforos:** 1x ESP32 / Arduino Uno (Gestión de LEDs y comunicación Serial).
* **Actuadores:** Módulos de Semáforos LED (Rojo, Amarillo, Verde).
* **Servidor de Procesamiento:** Laptop/PC corriendo el script de Python (detección YOLO).
* **Entorno de Prueba:** Maqueta vial a escala 1:64 (Vehículos Hotwheels).



##  Tecnologías de Software

| Componente | Tecnología | Uso |
| :--- | :--- | :--- |
| **IA / Visión** | YOLOv8 (Ultralytics) | Detección de objetos (autos) |
| **Backend/Frontend** | Python + Streamlit | Interfaz de usuario y lógica principal |
| **Comunicación** | PySerial & Requests | Comunicación Serial (PC-Arduino) y HTTPs (PC-Cámaras) |
| **Seguridad** | OpenSSL + Hashlib | Encriptación de video y autenticación |
| **Firmware** | C++ (Arduino IDE) | Código para ESP32S3 y Controlador de Semáforos |

## Estructura del Repositorio

```text
├──  arduino_code
│   ├── 📄 Traffic_Lights_Controller.ino   # Lógica de semáforos (Física)
│   └── 📄 XIAO_S3_HTTPS_Cam.ino           # Firmware de cámara segura
├──  models
│   └──  best.pt                         # Modelo YOLO entrenado (Weights)
├──  src
│   ├──  main.py                         # Código principal (Dashboard)
│   └── 🐍 https_test.py                   # Script de prueba de conexión segura
├── 📄 requirements.txt                    # Librerías necesarias
└── 📄 README.md                           # Documentación

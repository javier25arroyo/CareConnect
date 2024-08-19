# Proyecto para la Expocenfo 2024

## Propósito del Proyecto

Este proyecto ha sido desarrollado para la Expocenfo 2024 con el objetivo de demostrar el uso de sensores ultrasónicos HCSR04 para medir distancias y poder dar una conciencia  mas clara de la silla de ruedas con respecto a la posición de un objeto. El proyecto incluye la integración de un microcontrolador para procesar las lecturas del sensor y ajustar el ángulo del servo motor en función de las mediciones obtenidas.

## Cómo Utilizar el Proyecto

### Requisitos

- Microcontrolador compatible (IdeaBoard, ESP32, Arduino, etc.)
- Sensor ultrasónico (HCSR04 o HCSR05)
- Servo motor(MG90S micro servo)
- Cables de conexión
- Software de programación (Thonny, uPyCraft o Arduino IDE)

### Instrucciones de Uso

1. **Conexión del Hardware**:
    - Conecta el sensor HCSR04 al microcontrolador según el siguiente esquema:
        - VCC -> 5V
        - GND -> GND
        - TRIG -> Pin digital (board.IO27)
        - ECHO -> Pin digital (board.IO33)
    - Conecta el servo motor al microcontrolador:
        - VCC -> 5V
        - GND -> GND
        - Señal -> Pin PWM (board.IO4)

2. **Configuración del Software**:
    - Descarga e instala las bibliotecas necesarias para el sensor HCSR04 y el control del servo motor.
    - Carga el código proporcionado en el microcontrolador utilizando el software de programación.

3. **Ejecución del Proyecto**:
    - Una vez cargado el código, el microcontrolador comenzará a leer las distancias del sensor HCSR04 y ajustará el ángulo del servo motor en consecuencia.
    - Las lecturas de distancia se enviarán a una placa receptora y se imprimirán en la consola.

## Información Adicional

### Cómo Funciona

El proyecto utiliza un sensor ultrasónico HCSR04 para medir la distancia a un objeto. El microcontrolador procesa estas lecturas y ajusta el ángulo de un servo motor en función de las mediciones obtenidas. El código incluye técnicas para mejorar la precisión de las lecturas, como la toma de múltiples lecturas y el filtrado de valores atípicos.

### Código de Ejemplo

```python
import board
import pwmio
import time
from ideaboard import IdeaBoard
from hcsr04 import HCSR04

TIEMPO_ENTRE_LECTURAS = 1.0
NUM_LECTURAS = 5

servo_pin = board.IO4
pwm = pwmio.PWMOut(servo_pin, duty_cycle=0, frequency=100)
sonar = HCSR04(board.IO33, board.IO27)

def set_angle(angle):
    duty = int(65535 * (0.05 + (angle / 150) * 0.1))
    pwm.duty_cycle = duty

def mover_servo_continuo():
    while True:
        for angle in range(60, 160, 2):
            set_angle(angle)
            yield
            time.sleep(0.1)
        time.sleep(0.1)
        for angle in range(160, 60, -2):
            set_angle(angle)
            yield
            time.sleep(0.1)

def leer_distancia():
    distancias = []
    for _ in range(NUM_LECTURAS):
        dist = sonar.dist_cm()
        if dist is not None:
            distancias.append(dist)
        time.sleep(0.05)
    if distancias:
        distancias.sort()
        n = len(distancias)
        distancias = distancias[n//10 : -n//10]
        return sum(distancias) / len(distancias)
    else:
        return None

def main():
    servo_generator = mover_servo_continuo()
    last_distance_time = time.time()
    try:
        while True:
            next(servo_generator)
            current_time = time.time()
            if current_time - last_distance_time >= TIEMPO_ENTRE_LECTURAS:
                dist = leer_distancia()
                if dist is not None:
                    if dist > 100:
                        meters = int(dist // 100)
                        centimeters = dist % 100
                        distance_str = f"{meters}.{int(centimeters):02d} m"
                    else:
                        distance_str = f"{dist:.1f} cm"
                    esp.send(peer_mac, distance_str)
                    print(f"Distancia enviada: {distance_str}")
                else:
                    print("Error al leer la distancia del sensor.")
                last_distance_time = current_time
    except KeyboardInterrupt:
        pwm.deinit()

if __name__ == "__main__":
    main()


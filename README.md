# CareConect 2024

## Propósito del Proyecto

Este proyecto ha sido desarrollado para la Expocenfo 2024 con el objetivo de demostrar el uso de sensores ultrasónicos HCSR04 para medir distancias y poder dar una conciencia  mas clara de la silla de ruedas con respecto a la posición de un objeto. El proyecto incluye la integración de un microcontrolador para procesar las lecturas del sensor y ajustar el ángulo del servo motor en función de las mediciones obtenidas.

## Cómo Utilizar el Proyecto

### Requisitos

- Microcontrolador compatible (IdeaBoard, ESP32, Arduino, etc.)
- Sensor ultrasónico (HCSR04 o HCSR05)
- Servo motor(MG90S micro servo)
- Cables de conexión
- Placa receptora (para visualizar las lecturas de distancia)
- Pantalla LCD (LCD1604 16x4 Character LCD Display Module Blue Blacklight)
- Software de programación (Thonny, uPyCraft o Arduino IDE)

### Instrucciones de Uso

1. **Conexión del Hardware**:
    - Conecta el sensor HCSR04 al microcontrolador según el siguiente esquema:
        - VCC -> 3.3V
        - GND -> GND
        - TRIG -> Pin digital (board.IO27)
        - ECHO -> Pin digital (board.IO33)
    - Conecta el servo motor al microcontrolador:
        - VCC -> 3.3V
        - GND -> GND
        - Señal -> Pin PWM (board.IO4)
    - Conecta la placa receptora al microcontrolador para visualizar las lecturas de distancia.
    - Conecta la pantalla LCD al microcontrolador para visualizar las lecturas de distancia.
        - VCC -> 3.3V
        - GND -> GND
        - SDA -> Pin 21 (board.IO21)
        - SCL -> Pin 22 (board.IO22)

2. **Configuración del Software**:
    - Descarga e instala las bibliotecas necesarias para el sensor HCSR04 y el control del servo motor.
    - Carga el código proporcionado en el microcontrolador utilizando el software de programación.

3. **Ejecución del Proyecto**:
    - Una vez cargado el código, el microcontrolador comenzará a leer las distancias del sensor HCSR04 y ajustará el ángulo del servo motor en consecuencia.
    - Las lecturas de distancia se enviarán a una placa receptora y se imprimen en una pantalla LCD para su visualización.

## Información Adicional

### Cómo Funciona

El proyecto utiliza un sensor ultrasónico HCSR04 para medir la distancia a un objeto. El microcontrolador procesa estas lecturas y ajusta el ángulo de un servo motor en función de las mediciones obtenidas. El código incluye técnicas para mejorar la precisión de las lecturas, como la toma de múltiples lecturas y el filtrado de valores atípicos.

## Código para Controlar el Servo y Leer Distancia

### code1.py

Este código controla un servo y lee la distancia utilizando un sensor ultrasónico. El servo se mueve continuamente entre 60° y 160°, y el sensor ultrasónico toma múltiples lecturas para calcular una distancia promedio.

```python
import board
import pwmio
import time
import espnow
from ideaboard import IdeaBoard
from hcsr04 import HCSR04

# Configuración ESP-NOW
e = espnow.ESPNow()
peer = espnow.Peer(mac = b'\xd4\xd4\xda\x16\xb4\x9c')  
e.peers.append(peer)

TIEMPO_ENTRE_LECTURAS = 2.5
NUM_LECTURAS = 15
PROMEDIO_MOVIL_SIZE = 5
PAUSE_TIME = 0.1

# Configuración del pin PWM para el servo
servo_pin = board.IO4
pwm = pwmio.PWMOut(servo_pin, duty_cycle=0, frequency=100)

# Configuración del sensor HCSR04
sonar = HCSR04(board.IO33, board.IO27)

def set_angle(angle):
    """Ajusta el ángulo del servo."""
    duty = int(65535 * (0.05 + (angle / 150) * 0.1))
    pwm.duty_cycle = duty

def leer_distancia():
    """Lee la distancia del sensor con múltiples lecturas y filtrado."""
    distancias = []
    for _ in range(NUM_LECTURAS):
        dist = sonar.dist_cm()
        if dist is not None:
            distancias.append(dist)
        time.sleep(0.05)  # Pequeña pausa entre lecturas
    
    if distancias:
        distancias.sort()
        n = len(distancias)
        distancias = distancias[n//10 : -n//10]
        return sum(distancias) / len(distancias)
    else:
        return None

def mover_servo_continuo():
    """Generador que mueve el servo de 60° a 160° y viceversa de manera continua."""
    while True:
        for angle in range(40, 160, 2):
            set_angle(angle)
            yield
            time.sleep(PAUSE_TIME)
        for angle in range(160, 40, -2):
            set_angle(angle)
            yield
            time.sleep(PAUSE_TIME)

def main():
    last_distance_time = time.time()
    lecturas = []
    servo_generator = mover_servo_continuo()

    try:
        while True:
            # Verifica si han pasado 2 segundos para leer la distancia
            current_time = time.time()
            if current_time - last_distance_time >= TIEMPO_ENTRE_LECTURAS:
                distancia = leer_distancia()
                if distancia is not None:
                    lecturas.append(distancia)
                    if len(lecturas) > PROMEDIO_MOVIL_SIZE:
                        lecturas.pop(0)
                    promedio_distancia = sum(lecturas) / len(lecturas)
                    
                    if promedio_distancia > 100:
                        meters = int(promedio_distancia // 100)
                        centimeters = promedio_distancia % 100
                        mensaje = f"Dist: {meters}.{int(centimeters):02d} m"
                    else:
                        mensaje = f"Dist: {promedio_distancia:.1f} cm"
                    
                    print(mensaje)
                    e.send(mensaje.encode())  # Enviar el mensaje a través de ESP-NOW
                else:
                    print("Error en lectura.")
                last_distance_time = current_time
            
            # Mover el servo
            next(servo_generator)
            
            # Pequeña pausa antes de la siguiente lectura del sensor
            time.sleep(0.01)
    except KeyboardInterrupt:
        pwm.deinit()

if __name__ == "__main__":
    main()
```

## Codigos para la Placa Receptora

### code2.py

Este código recibe las lecturas de distancia enviadas por el microcontrolador y las muestra en la pantalla LCD.

```python

# Importar las bibliotecas necesarias
import espnow
import time
import board
from lcd import LCD
from i2c_pcf8574_interface import I2CPCF8574Interface
from lcd import CursorMode

TIEMPO_ENTRE_LECTURAS = 2.5

# Configuración de ESP-NOW
e = espnow.ESPNow()
i2c = board.I2C()
lcd_columns = 16
lcd_rows = 4
lcd = LCD(I2CPCF8574Interface(i2c, 0x27), num_rows=lcd_rows, num_cols=lcd_columns)

# Lista para almacenar los paquetes recibidos
packets = []
last_print_time = time.time()


# Bucle principal para leer y mostrar las lecturas de distancia
while True:
    try:
        if e:
            packet = e.read()
            if packet:
                message = packet.msg.decode()
                packets.append(message)

                # Solo imprimir la distancia cada 2.5 segundos
                current_time = time.time()
                if current_time - last_print_time >= 2.5:
                    lcd.clear()
                    lcd.set_cursor_pos(0, 0)
                    lcd.print(message[:16])

                    if len(message) > 16:
                        lcd.set_cursor_pos(1, 0)
                        lcd.print(message[16:32])

                    print(f"Distancia: {message}")  # Imprimir solo la distancia en la consola
                    last_print_time = current_time

                time.sleep(0.1)
    except Exception as e:
        print(f"Error: {e}")
        time.sleep(TIEMPO_ENTRE_LECTURAS)  # Esperar 2.5 segundos antes de intentar nuevamente
```
    

# CareConect 2024

## Project Purpose

This project was developed for Expocenfo 2024 with the goal of demonstrating the use of ultrasonic sensors (HCSR04) to measure distances and provide clearer awareness of a wheelchair's position relative to an object. The project includes the integration of a microcontroller to process sensor readings and adjust the angle of a servo motor based on the measurements obtained.

## How to Use the Project

### Requirements

- Compatible microcontroller (IdeaBoard, ESP32, Arduino, etc.)
- Ultrasonic sensor (HCSR04 or HCSR05)
- Servo motor (MG90S micro servo)
- Connection cables
- Receiving board (to display distance readings)
- LCD screen (LCD1604 16x4 Character LCD Display Module Blue Blacklight)
- Programming software (Thonny, uPyCraft, or Arduino IDE)

### Usage Instructions

1. **Hardware Connection**:
    - Connect the HCSR04 sensor to the microcontroller according to the following scheme:
        - VCC -> 3.3V
        - GND -> GND
        - TRIG -> Digital pin (board.IO27)
        - ECHO -> Digital pin (board.IO33)
    - Connect the servo motor to the microcontroller:
        - VCC -> 3.3V
        - GND -> GND
        - Signal -> PWM pin (board.IO4)
    - Connect the receiving board to the microcontroller to display distance readings.
    - Connect the LCD screen to the microcontroller to display distance readings.
        - VCC -> 3.3V
        - GND -> GND
        - SDA -> Pin 21 (board.IO21)
        - SCL -> Pin 22 (board.IO22)

2. **Software Configuration**:
    - Download and install the necessary libraries for the HCSR04 sensor and servo motor control.
    - Upload the provided code to the microcontroller using the programming software.

3. **Project Execution**:
    - Once the code is uploaded, the microcontroller will start reading distances from the HCSR04 sensor and adjust the servo motor angle accordingly.
    - Distance readings will be sent to a receiving board and printed on an LCD screen for visualization.

## Additional Information

### How It Works

The project uses an HCSR04 ultrasonic sensor to measure the distance to an object. The microcontroller processes these readings and adjusts the angle of a servo motor based on the measurements obtained. The code includes techniques to improve the accuracy of the readings, such as taking multiple readings and filtering out outlier values.

## Code to Control the Servo and Read Distance

### code1.py

This code controls a servo and reads the distance using an ultrasonic sensor. The servo continuously moves between 60° and 160°, and the ultrasonic sensor takes multiple readings to calculate an average distance.

```python
import board
import pwmio
import time
import espnow
from ideaboard import IdeaBoard
from hcsr04 import HCSR04

# Configuración ESP-NOW
e = espnow.ESPNow()
peer = espnow.Peer(mac = b'\xd4\xd4\xda\x16\xb4\x9c')  
e.peers.append(peer)

TIEMPO_ENTRE_LECTURAS = 2.5
NUM_LECTURAS = 15
PROMEDIO_MOVIL_SIZE = 5
PAUSE_TIME = 0.1

# PWM pin configuration for the servo
servo_pin = board.IO4
pwm = pwmio.PWMOut(servo_pin, duty_cycle=0, frequency=100)

# HCSR04 Sensor Configuration
sonar = HCSR04(board.IO33, board.IO27)

def set_angle(angle):
    """Ajusta el ángulo del servo."""
    duty = int(65535 * (0.05 + (angle / 150) * 0.1))
    pwm.duty_cycle = duty

def leer_distancia():
    """Read the distance from the sensor with multiple readings and filtering."""
    distancias = []
    for _ in range(NUM_LECTURAS):
        dist = sonar.dist_cm()
        if dist is not None:
            distancias.append(dist)
        time.sleep(0.05)  # Pequeña pausa entre lecturas
    
    if distancias:
        distancias.sort()
        n = len(distancias)
        distancias = distancias[n//10 : -n//10]
        return sum(distancias) / len(distancias)
    else:
        return None

def mover_servo_continuo():
    """Generator that moves the servo from 60° to 160° and vice versa continuously"""
    while True:
        for angle in range(40, 160, 2):
            set_angle(angle)
            yield
            time.sleep(PAUSE_TIME)
        for angle in range(160, 40, -2):
            set_angle(angle)
            yield
            time.sleep(PAUSE_TIME)

def main():
    last_distance_time = time.time()
    lecturas = []
    servo_generator = mover_servo_continuo()

    try:
        while True:
            # Check if 2 seconds have passed to read the distance
            current_time = time.time()
            if current_time - last_distance_time >= TIEMPO_ENTRE_LECTURAS:
                distancia = leer_distancia()
                if distancia is not None:
                    lecturas.append(distancia)
                    if len(lecturas) > PROMEDIO_MOVIL_SIZE:
                        lecturas.pop(0)
                    promedio_distancia = sum(lecturas) / len(lecturas)
                    
                    if promedio_distancia > 100:
                        meters = int(promedio_distancia // 100)
                        centimeters = promedio_distancia % 100
                        mensaje = f"Dist: {meters}.{int(centimeters):02d} m"
                    else:
                        mensaje = f"Dist: {promedio_distancia:.1f} cm"
                    
                    print(mensaje)
                    e.send(mensaje.encode())  # Enviar el mensaje a través de ESP-NOW
                else:
                    print("Error en lectura.")
                last_distance_time = current_time
            
            # Move the servo
            next(servo_generator)
            
            # Short pause before next sensor reading
            time.sleep(0.01)
    except KeyboardInterrupt:
        pwm.deinit()

if __name__ == "__main__":
    main()

```

## Codes for the Receiving Board

### code2.py

This code receives distance readings sent by the microcontroller and displays them on the LCD screen.

```python


# Import the necessary libraries
import espnow
import time
import board
from lcd import LCD
from i2c_pcf8574_interface import I2CPCF8574Interface
from lcd import CursorMode

TIEMPO_ENTRE_LECTURAS = 2.5

# ESP-NOW configuration
e = espnow.ESPNow()
i2c = board.I2C()
lcd_columns = 16
lcd_rows = 4
lcd = LCD(I2CPCF8574Interface(i2c, 0x27), num_rows=lcd_rows, num_cols=lcd_columns)

# List to store received packets
packets = []
last_print_time = time.time()

# Main loop to read and display distance readings
while True:
    try:
        if e:
            packet = e.read()
            if packet:
                message = packet.msg.decode()
                packets.append(message)

                # Only print the distance every 2.5 seconds
                current_time = time.time()
                if current_time - last_print_time >= 2.5:
                    lcd.clear()
                    lcd.set_cursor_pos(0, 0)
                    lcd.print(message[:16])

                    if len(message) > 16:
                        lcd.set_cursor_pos(1, 0)
                        lcd.print(message[16:32])

                    print(f"Distancia: {message}")  # Print only the distance to the console
                    last_print_time = current_time

                time.sleep(0.1)
    except Exception as e:
        print(f"Error: {e}")
        time.sleep(TIEMPO_ENTRE_LECTURAS)  # Wait 2.5 seconds before trying again
```


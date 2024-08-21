# Proyecto para la Expocenfo 2024

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
from ideaboard import IdeaBoard
from hcsr04 import HCSR04

TIEMPO_ENTRE_LECTURAS = 2
NUM_LECTURAS = 20

# Configuración del pin PWM para el servo
servo_pin = board.IO4
pwm = pwmio.PWMOut(servo_pin, duty_cycle=0, frequency=50)  # Asegúrate de que la frecuencia sea correcta para tu servo

# Configuración del sensor HCSR04
sonar = HCSR04(board.IO33, board.IO27)

def set_angle(angle):
    """Ajusta el ángulo del servo.
    
    Calcula el ciclo de trabajo (duty cycle) necesario para ajustar el ángulo del servo y lo aplica.
    """
    duty = int(65535 * (0.05 + (angle / 150) * 0.1))
    pwm.duty_cycle = duty

def mover_servo_continuo():
    """Generador que mueve el servo de 60° a 160° y viceversa de manera continua.
    
    Este generador mueve el servo en pasos de 2 grados desde 60° hasta 160° y luego de vuelta a 60°.
    """
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
    """Lee la distancia del sensor con múltiples lecturas y filtrado.
    
    Toma múltiples lecturas del sensor ultrasónico, filtra los valores atípicos y calcula el promedio de las lecturas restantes.
    """
    distancias = []
    for _ in range(NUM_LECTURAS):
        dist = sonar.dist_cm()
        if dist is not None:
            distancias.append(dist)
        time.sleep(0.05)  # Pequeña pausa entre lecturas
    
    if distancias:
        # Filtra las lecturas eliminando valores atípicos
        distancias.sort()
        # Elimina el 10% superior e inferior de las lecturas
        n = len(distancias)
        distancias = distancias[n//10 : -n//10]
        # Calcula el promedio de las lecturas restantes
        return sum(distancias) / len(distancias)
    else:
        return None

def main():
    servo_generator = mover_servo_continuo()
    last_distance_time = time.time()

    try:
        while True:
            # Mueve el servo un paso
            next(servo_generator)
            
            # Verifica si han pasado 2 segundos para leer la distancia
            current_time = time.time()
            if current_time - last_distance_time >= TIEMPO_ENTRE_LECTURAS:
                dist = leer_distancia()
                if dist is not None:
                    if dist > 100:
                        meters = int(dist // 100)
                        centimeters = dist % 100
                        distance_str = f"Dist: {meters}.{int(centimeters):02d} m"
                    else:
                        distance_str = f"Dist: {dist:.1f} cm"
                    print(distance_str)
                else:
                    print("Error en lectura.")
                last_distance_time = current_time
            
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
# Project for Expocenfo 2024

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
from ideaboard import IdeaBoard
from hcsr04 import HCSR04

READING_INTERVAL = 2
NUM_READINGS = 20

# PWM pin configuration for the servo
servo_pin = board.IO4
pwm = pwmio.PWMOut(servo_pin, duty_cycle=0, frequency=50)  # Ensure the frequency is correct for your servo

# HCSR04 sensor configuration
sonar = HCSR04(board.IO33, board.IO27)

def set_angle(angle):
    """Adjusts the servo angle.
    
    Calculates the duty cycle needed to set the servo angle and applies it.
    """
    duty = int(65535 * (0.05 + (angle / 150) * 0.1))
    pwm.duty_cycle = duty

def move_servo_continuous():
    """Generator that continuously moves the servo from 60° to 160° and back.
    
    This generator moves the servo in 2-degree steps from 60° to 160° and then back to 60°.
    """
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

def read_distance():
    """Reads the distance from the sensor with multiple readings and filtering.
    
    Takes multiple readings from the ultrasonic sensor, filters outliers, and calculates the average of the remaining readings.
    """
    distances = []
    for _ in range(NUM_READINGS):
        dist = sonar.dist_cm()
        if dist is not None:
            distances.append(dist)
        time.sleep(0.05)  # Small pause between readings
    
    if distances:
        # Filter readings by removing outliers
        distances.sort()
        # Remove the top and bottom 10% of readings
        n = len(distances)
        distances = distances[n//10 : -n//10]
        # Calculate the average of the remaining readings
        return sum(distances) / len(distances)
    else:
        return None

def main():
    servo_generator = move_servo_continuous()
    last_distance_time = time.time()

    try:
        while True:
            # Move the servo one step
            next(servo_generator)
            
            # Check if 2 seconds have passed to read the distance
            current_time = time.time()
            if current_time - last_distance_time >= READING_INTERVAL:
                dist = read_distance()
                if dist is not None:
                    if dist > 100:
                        meters = int(dist // 100)
                        centimeters = dist % 100
                        distance_str = f"Dist: {meters}.{int(centimeters):02d} m"
                    else:
                        distance_str = f"Dist: {dist:.1f} cm"
                    print(distance_str)
                else:
                    print("Error in reading.")
                last_distance_time = current_time
            
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

[]: # (END)
```markdown

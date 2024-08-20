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
        - VCC -> 5V
        - GND -> GND
        - TRIG -> Pin digital (board.IO27)
        - ECHO -> Pin digital (board.IO33)
    - Conecta el servo motor al microcontrolador:
        - VCC -> 5V
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
import board
import busio
import time
import adafruit_character_lcd.character_lcd_i2c as character_lcd

# Configurar ESP-NOW
e = espnow.ESPNow()

# Configurar la pantalla LCD
i2c = busio.I2C(board.SCL, board.SDA)
lcd_columns = 16
lcd_rows = 4
lcd = character_lcd.Character_LCD_I2C(i2c, lcd_columns, lcd_rows)

packets = []

while True:
    if e:
       # Leer el paquete de ESP-NOW
        packet = e.read()
        if packet:
            # Decodificar el mensaje del paquete.
            message = packet.msg.decode()
            packets.append(message)
            lcd.clear()
            lcd.message = message  # Mostrar el mensaje en la pantalla LCD.
            print(message)  # Imprime el mensaje a la consola.
            time.sleep(0.1)
            time.sleep(0.1)
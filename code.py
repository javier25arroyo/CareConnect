import board
from ideaboard import IdeaBoard
from time import sleep
from hcsr04 import HCSR04
import pwmio
import socketpool
import ssl
import wifi 

# Configuración del servo motor (pin 4)
servo = board.IO4
pwm = pwmio.PWMOut(servo_pin, duty_cycle=0, frequency=50)

# Configuración del sensor de distancia HC-SR04
                # echo       trig
sonar = HCSR04(board.IO33 ,board.IO27)

# Configuración de Wi-Fi
print("Connecting to WiFi...")
wifi.radio.connect("wifi", "password")  # Reemplaza con tus credenciales
print("Connected!")

# Variables para comparar la posición
distancia_anterior = 0

def mover_servo(angulo):
    """Mueve el servo al ángulo especificado (0-180 grados)."""
    duty_cycle = int(2 ** 15 + 2 ** 15 * (angulo / 180))
    pwm.duty_cycle = duty_cycle

while True:
    try:
        # Medición de distancia con el sensor HC-SR04
        dist = sonar.distance
        # Verifica si la distancia ha cambiado
        if abs(dist - distancia_anterior) > 5:
            print(f"La posición ha cambiado. Nueva distancia: {dist} cm")
        distancia_anterior = dist

        print("Distancia:", dist)

        # Movimiento del servo de 0 a 45 grados en incrementos de 2 grados
        for angulo in range(0, 46, 2):
            mover_servo(angulo)
            time.sleep(0.1)  # 100 milisegundos
    except RuntimeError as e:
        print(f"Error: {e}")
    except Exception as e:
        print(f"Error desconocido: {e}")  # type: ignore
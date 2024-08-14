import board
import pwmio
import time
from ideaboard import IdeaBoard
from time import sleep
from hcsr04 import HCSR04

# Configuracion del servo
servo = board-IO4
pwm = pwmio.PWMOut(servo, duty_cycle=0, frequency=50)

# Configuracion del sensor de distancia HC-SR04
                #echo       trig    
sonar = HCSR04(board.IO33, board.IO27)

# Variables para comparar la posicion
dist_anterior = 0

def set_angle(angle):
    """Mueve el servo al angulo especificado (0-180 grados)."""
    duty_cycle = int(2**15 + 2**15 * (angle / 180))
    pwm.duty_cycle = duty_cycle

while True:
    try:
        # Medicion de distancia con el sensor HC-SR04
        dist = sonar.distance
        # Verifica si la distancia ha cambiado
        if abs(dist - dist_anterior) > 5:
            print(f"La posicion ha cambiado. Nueva distancia: {dist} cm")
        dist_anterior = dist

        print("Distancia:", dist)

        # Movimiento del servo de 0 a 45 grados en incrementos de 2 grados
        for angulo in range(0, 46, 2):
            set_angle(angulo)
            time.sleep(0.1)  # 100 milisegundos
    except RuntimeError as e:
        print(f"Error: {e}")
    except Exception as e:
        print(f"Error desconocido: {e}")  # type: ignore

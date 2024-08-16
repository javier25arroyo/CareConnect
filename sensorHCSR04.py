import board
import pwmio
import time
from ideaboard import IdeaBoard
from hcsr04 import HCSR04

# Configuración del pin PWM para el servo
servo_pin = board.IO4
pwm = pwmio.PWMOut(servo_pin, duty_cycle=0, frequency=100)

# Función para ajustar el ángulo del servo
def set_angle(angle):
    duty = int(65535 * (0.05 + (angle / 150) * 0.1))
    pwm.duty_cycle = duty

# Configuración del sensor HCSR04
sonar = HCSR04(board.IO33, board.IO27)

try:
    while True:
        # Leer la distancia del sensor
        dist = sonar.dist_cm()
        print(dist, "cm")
        
        # Mover el servo de 60° a 160° y viceversa
        for angle in range(60, 160, 2):
            set_angle(angle)
            time.sleep(0.1)
        
        time.sleep(0.1)
        
        for angle in range(160, 60, -2):
            set_angle(angle)
            time.sleep(0.1)
        
        # Pequeña pausa antes de la siguiente lectura del sensor
        time.sleep(0.2)
        
except KeyboardInterrupt:
    pwm.deinit()


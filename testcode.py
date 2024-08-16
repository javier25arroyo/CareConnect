import board
import pwmio
import time
from time import sleep
from ideaboard import IdeaBoard
from hcsr04 import HCSR04

# Constantes
SERVO = board.IO4
TRIGG = board.IO33
ECHO = board.IO27
FREQUENCY = 100
DUTY_CYCLE = 0
ANGLE_STEP = 2
MIN_ANGLE = 60
MAX_ANGLE = 160
PAUSE_TIME = 0.1
SENSOR_PAUSE = 0.2

# Configuración del pin PWM para el servo
pwm = pwmio.PWMOut(SERVO, duty_cycle=DUTY_CYCLE, frequency=FREQUENCY)

# Configuración del sensor HCSR04
sonar = HCSR04(TRIGG, ECHO)

def set_angle(angle):
    """Ajusta el ángulo del servo."""
    duty = int(65535 * (0.05 + (angle / 150) * 0.1))
    pwm.duty_cycle = duty

def leer_distancia():
    """Lee la distancia del sensor HCSR04."""
    return sonar.dist_cm()

def mover_servo():
    """Mueve el servo de MIN_ANGLE a MAX_ANGLE y viceversa."""
    for angle in range(MIN_ANGLE, MAX_ANGLE, ANGLE_STEP):
        set_angle(angle)
        time.sleep(PAUSE_TIME)
    
    time.sleep(PAUSE_TIME)
    
    for angle in range(MAX_ANGLE, MIN_ANGLE, -ANGLE_STEP):
        set_angle(angle)
        time.sleep(PAUSE_TIME)

def main():
    try:
        while True:
            # Leer la distancia del sensor
            distancia = leer_distancia()
            print(f"Distancia: {distancia} cm")
            
            # Mover el servo
            mover_servo()
            
            # Pequeña pausa antes de la siguiente lectura del sensor
            time.sleep(SENSOR_PAUSE)
    except KeyboardInterrupt:
        pwm.deinit()

if __name__ == "__main__":
    main()
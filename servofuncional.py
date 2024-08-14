import board
import pwmio
import time

# Configuración del pin PWM
servo_pin = board.IO4
pwm = pwmio.PWMOut(servo_pin, duty_cycle=0, frequency= 100)

def set_angle(angle):
    # Convertir el ángulo a ciclo de trabajo (duty cycle)
    duty = int(65535 * (0.05 + (angle / 150) * 0.1))
    pwm.duty_cycle = duty

try:
    while True:
        # Mover el servo de 60° a 160°
        for angle in range(60, 160, 2):
            set_angle(angle)
            time.sleep(0.1)
        
        # Reducir el tiempo de espera en la posición de 180°
        time.sleep(0.1)
        
        # Mover el servo de 160° a 60°
        for angle in range(160, 60, -2):
            set_angle(angle)
            time.sleep(0.1)
except KeyboardInterrupt:
    pwm.deinit()
import board
import pwmio
import time
from ideaboard import IdeaBoard
from hcsr04 import HCSR04

TIEMPO_ENTRE_LECTURAS = 2
NUM_REINTENTOS = 3

# Configuración del pin PWM para el servo
servo_pin = board.IO4
pwm = pwmio.PWMOut(servo_pin, duty_cycle=0, frequency=100)

# Configuración del sensor HCSR04
sonar = HCSR04(board.IO33, board.IO27)

def set_angle(angle):
    """Ajusta el ángulo del servo."""
    duty = int(65535 * (0.05 + (angle / 150) * 0.1))
    pwm.duty_cycle = duty

def mover_servo_continuo():
    """Generador que mueve el servo de 60° a 160° y viceversa de manera continua."""
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
    """Lee la distancia del sensor con reintentos y filtrado."""
    distancias = []
    for _ in range(NUM_REINTENTOS):
        dist = sonar.dist_cm()
        if dist is not None:
            distancias.append(dist)
        time.sleep(0.1)
    
    if distancias:
        # Filtra las lecturas eliminando valores atípicos
        distancias.sort()
        return distancias[len(distancias) // 2]  # Devuelve la mediana
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
                        distance_str = f"{meters}.{int(centimeters):02d} m"
                    else:
                        distance_str = f"{dist:.1f} cm"
                    # Enviar la distancia a la placa receptora
                    esp.send(peer_mac, distance_str)
                    print(f"Distancia enviada: {distance_str}")
                else:
                    print("Error al leer la distancia del sensor.")
                
                last_distance_time = current_time

    except KeyboardInterrupt:
        pwm.deinit()

if __name__ == "__main__":
    main()
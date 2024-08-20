import board
import pwmio
import time
import espnow
from ideaboard import IdeaBoard
from hcsr04 import HCSR04

# Configuración ESP-NOW
e = espnow.ESPNow()
peer = espnow.Peer(mac=b'\x80\xdo\x11\x0e\xa0')  # Reemplaza con la dirección MAC de la tarjeta receptora
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
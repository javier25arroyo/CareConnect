import board
import pwmio
import time
from ideaboard import IdeaBoard
from hcsr04 import HCSR04
import espnow
import wifi

TIEMPO_ENTRE_LECTURAS = 2
NUM_LECTURAS = 20

# Configuración del pin PWM para el servo
servo_pin = board.IO4
pwm = pwmio.PWMOut(servo_pin, duty_cycle=0, frequency=50)  # Asegúrate de que la frecuencia sea correcta para tu servo

# Configuración del sensor HCSR04
sonar = HCSR04(board.IO33, board.IO27)

# Configuración de ESP-NOW
wifi.radio.enabled = True
esp = espnow.ESPNow()
esp.active(True)

# Dirección MAC del receptor (reemplaza con la dirección MAC de tu dispositivo receptor)
peer_mac = b'\x24\x0A\xC4\x12\x34\x56'
esp.add_peer(peer_mac)

def set_angle(angle):
    """Ajusta el ángulo del servo."""
    if 0 <= angle <= 180:  # Asegúrate de que el ángulo esté dentro del rango permitido
        duty = int(65535 * (0.05 + (angle / 180) * 0.1))
        pwm.duty_cycle = duty
        print(f"Ángulo ajustado a: {angle} grados, ciclo de trabajo: {duty}")
    else:
        print(f"Ángulo fuera de rango: {angle}")

def mover_servo_continuo():
    """Generador que mueve el servo de 60° a 160° y viceversa de manera continua."""
    while True:
        for angle in range(60, 160, 1):  # Pasos más pequeños para un movimiento más suave
            set_angle(angle)
            yield
            time.sleep(0.05)  # Pausa más corta para aumentar la velocidad
        
        time.sleep(0.05)
        
        for angle in range(160, 60, -1):  # Pasos más pequeños para un movimiento más suave
            set_angle(angle)
            yield
            time.sleep(0.05)  # Pausa más corta para aumentar la velocidad

def leer_distancia():
    """Lee la distancia del sensor con múltiples lecturas y filtrado."""
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
                    # Enviar la distancia a través de ESP-NOW
                    esp.send(peer_mac, distance_str.encode('utf-8'))
                else:
                    print("Error en lectura.")
                last_distance_time = current_time
            
    except KeyboardInterrupt:
        pwm.deinit()
            
if __name__ == "__main__":
    main()
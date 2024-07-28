import board
import time
import pwmio
import adafruit_hcsr04
import adafruit_mpu6050
import socketpool
import ssl
import wifi
import adafruit_requests as requests

# Configuración del servo motor (pin 4)
servo_pin = board.IO4
pwm = pwmio.PWMOut(servo_pin, duty_cycle=2 ** 15, frequency=50)

# Configuración del sensor de distancia HC-SR04
trig = board.IO33
echo = board.IO27
sonar = adafruit_hcsr04.HCSR04(trig, echo)

# Configuración del giroscopio MPU6050 (pines I2C por defecto: 21 y 22)
i2c = board.I2C()
mpu = adafruit_mpu6050.MPU6050(i2c)

# Configuración de Wi-Fi
print("Connecting to WiFi...")
wifi.radio.connect("sspi", "password")  # Reemplaza con tus credenciales
print("Connected!")

# Variables para comparar la posición
distancia_anterior = 0

# Umbral de velocidad angular para detectar movimiento exponencial
UMBRAL_VELOCIDAD_ANGULAR = 50

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

        # Lecturas del sensor MPU6050
        accel_x, accel_y, accel_z = mpu.acceleration
        gyro_x, gyro_y, gyro_z = mpu.gyro

        # Calcula la velocidad angular total
        velocidad_angular_total = abs(gyro_x) + abs(gyro_y) + abs(gyro_z)

        # Verifica si la velocidad angular supera el umbral
        if velocidad_angular_total > UMBRAL_VELOCIDAD_ANGULAR:
            print(f"¡Movimiento exponencial detectado! Velocidad angular total: {velocidad_angular_total} grados/s")

        print("Aceleración (m/s^2):", accel_x, accel_y, accel_z)
        print("Direccion de la silla (grados/s):", gyro_x, gyro_y, gyro_z)
        print("Distancia:", dist)

        # Movimiento del servo de 0 a 45 grados en incrementos de 2 grados
        for angulo in range(0, 46, 2):
            mover_servo(angulo)
            time.sleep(0.1)  # 100 milisegundos
    except RuntimeError as e:
        print(f"Error: {e}")
    except Exception as e:
        print(f"Error desconocido: {e}") # type: ignore
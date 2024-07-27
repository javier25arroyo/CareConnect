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

# Configuración de Telegram
TELEGRAM_BOT_TOKEN = "6420443163:AAG0SXFNkEMq5sB2EPyabrY6S9mGPk7W808"
TELEGRAM_CHAT_ID = 5880741389

# Variables para comparar la posición
distancia_anterior = 0

# Umbral de velocidad angular para detectar movimiento exponencial
UMBRAL_VELOCIDAD_ANGULAR = 50

def enviar_mensaje_telegram(mensaje):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    parametros = {
        'chat_id': TELEGRAM_CHAT_ID,
        'text': mensaje
    }
    try:
        response = requests.post(url, json=parametros)
        if response.status_code == 200:
            print("Mensaje enviado a Telegram")
        else:
            print(f"Error al enviar el mensaje a Telegram. Status code: {response.status_code}")
    except Exception as e:
        print(f"Error desconocido: {e}")

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
            mensaje = f"La posición ha cambiado. Nueva distancia: {dist} cm"
            enviar_mensaje_telegram(mensaje)

        distancia_anterior = dist

        # Lecturas del sensor MPU6050
        accel_x, accel_y, accel_z = mpu.acceleration
        gyro_x, gyro_y, gyro_z = mpu.gyro

        # Calcula la velocidad angular total
        velocidad_angular_total = abs(gyro_x) + abs(gyro_y) + abs(gyro_z)

        # Verifica si la velocidad angular supera el umbral
        if velocidad_angular_total > UMBRAL_VELOCIDAD_ANGULAR:
            mensaje_giroscopio = f"¡Movimiento exponencial detectado! Velocidad angular total: {velocidad_angular_total} grados/s"
            enviar_mensaje_telegram(mensaje_giroscopio)

        print("Aceleración (m/s^2):", accel_x, accel_y, accel_z)
        print("Direccion de la silla (grados/s):", gyro_x, gyro_y, gyro_z)
        print("Distancia:", dist)

        # Movimiento del servo de 0 a 100 grados
        for angulo in range(0, 101, 10):
            mover_servo(angulo)
            time.sleep(0.1)

    except RuntimeError as e:
        print(f"Error: {e}")
    except Exception as e:
        print(f"Error desconocido: {e}")

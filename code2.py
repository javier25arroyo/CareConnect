import espnow
import wifi

# Configuración de ESPNOW
wifi.radio.enabled = True
esp = espnow.ESPNow()
esp.active(True)

# Dirección MAC de la placa emisora
peer_mac = b'\xd4\xd4\xda\x16il'  # Reemplaza con la dirección MAC de la placa emisora
esp.add_peer(peer_mac)

try:
    while True:
        # Recibir la distancia desde la placa emisora
        host, msg = esp.recv()
        if msg:
            dist = float(msg)
            print(f"Distancia recibida: {dist:.2f} cm")

except KeyboardInterrupt:
    pass
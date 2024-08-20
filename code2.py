import espnow
import board
import busio
import time
import adafruit_character_lcd.character_lcd_i2c as character_lcd

# Configuración de ESP-NOW
e = espnow.ESPNow()

# Configuración de la pantalla LCD
i2c = busio.I2C(board.IO22, board.IO21)
lcd_columns = 16
lcd_rows = 4
lcd = character_lcd.Character_LCD_I2C(i2c, lcd_columns, lcd_rows)

packets = []

while True:
    if e:
        packet = e.read()
        if packet:
            message = packet.msg.decode()
            packets.append(message)
            lcd.clear()
            lcd.message = message  # Mostrar el mensaje en la pantalla LCD
            print(message)  # Imprimir el mensaje en la consola
        time.sleep(0.1)
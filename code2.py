import espnow
import time
import board
from lcd import LCD
from i2c_pcf8574_interface import I2CPCF8574Interface
from lcd import CursorMode

TIEMPO_ENTRE_LECTURAS = 2.5

e = espnow.ESPNow()
i2c = board.I2C()
lcd_columns = 16
lcd_rows = 4
lcd = LCD(I2CPCF8574Interface(i2c, 0x27), num_rows=lcd_rows, num_cols=lcd_columns)

packets = []
last_print_time = time.time()

while True:
    try:
        if e:
            packet = e.read()
            if packet:
                message = packet.msg.decode()
                packets.append(message)

                # Solo imprimir la distancia cada 2.5 segundos
                current_time = time.time()
                if current_time - last_print_time >= 2.5:
                    lcd.clear()
                    lcd.set_cursor_pos(0, 0)
                    lcd.print(message[:16])

                    if len(message) > 16:
                        lcd.set_cursor_pos(1, 0)
                        lcd.print(message[16:32])

                    print(f"Distancia: {message}")  # Imprimir solo la distancia en la consola
                    last_print_time = current_time

                time.sleep(0.1)
    except Exception as e:
        print(f"Error: {e}")
        time.sleep(TIEMPO_ENTRE_LECTURAS)  # Esperar 2.5 segundos antes de intentar nuevamente
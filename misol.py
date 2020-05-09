# 09.05.2020 v1.0 miSol meteo-station

import logging
import time
import requests

from serial import Serial

logging.basicConfig(
    level=logging.WARNING, filename='/misol/log.log', filemode='w',
    format="%(asctime)s %(levelname)s [%(name)s] %(message)s")
log = logging.getLogger(__name__)

def main():
    try:
        s = Serial('COM3', 9600, timeout=60)

        while True:
            raw = s.read(21)

            checksum = sum(i for i in raw[:16]) & 0xFF
            assert checksum == raw[16], "Wrong checksum"

            TX = raw[0]
            SC = raw[1]
            WD = raw[2]
            TP8 = raw[3] & 0b00001111
            TP = (((TP8 << 8) + raw[4]) - 400) / 10
            HM = raw[5]
            WS = (raw[6] / 8 ) * 1.12
            WG = raw[7] * 1.12
            RN = (raw[8] << 8) + raw[9]
            UV = (raw[10] << 8) + raw[11]
            LT = ((raw[12] << 16) + (raw[13] << 8) + (raw[14]))/10
            BT = raw[15]
            PS = ((raw[17] << 16) + (raw[18] << 8) + (raw[19]))/100
            PS_checksum = sum(i for i in raw[17:20]) & 0xFF
            assert PS_checksum == raw[20], "Wrong barometric checksum"

            payload = {
                    'wind_direction': WD,
                    'humidity': HM,
                    'temperature': TP,
                    'wind_speed': WS,
                    'wind_gusts': WG,
                    'rain': RN,
                    'uvi': UV,
                    'light': LT,
                    'battery': BT,
                    'pressure': PS,
                    'last_update': int(time.time())
                }

            try:
                response = requests.get('https://unqb.ru/meteo/', params=payload, verify=False)
                response.raise_for_status()
            except requests.HTTPError as http_err:
                log.warning(f'HTTP error occurred: {http_err}')
            except Exception as err:
                log.warning(f'Other error occurred: {err}')

    except AssertionError as e:
        log.error(e)

    except:
        log.exception("Exception")


if __name__ == '__main__':
    main()

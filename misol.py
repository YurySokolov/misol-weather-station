# !/usr/bin/env python3
#
# disp.py - read from Fine Offset RS495 weather station.
# Take RS485 via USB message from a Fine Offset WH2950 and interpret.
# See https://wordpress.com/post/doughall.me/1683
#
# Copyright (C) 2018, Doug Hall
# Licensed under MIT license, see included file LICENSE or http://opensource.org/licenses/MIT

import logging
import time

from paho.mqtt.client import Client, MQTT_ERR_SUCCESS
from serial import Serial

from wdata import RawWeatherData, wdata


def publish(client: Client, topic: str, order: int):
    client.publish(f"{BASE}/{topic}/meta/type", "value", qos=0, retain=True)
    client.publish(f"{BASE}/{topic}/meta/readonly", 1, qos=0, retain=True)
    client.publish(f"{BASE}/{topic}/meta/order", order, qos=0, retain=True)


logging.basicConfig(
    level=logging.DEBUG, filename='/misol/log.log', filemode='w',
    format="%(asctime)s %(levelname)s [%(name)s] %(message)s")
log = logging.getLogger(__name__)

BASE = '/devices/misol/controls'
TOPICS = ['temperature', 'humidity', 'light', 'wind_direction', 'wind_speed',
          'wind_gust', 'rain', 'uvi', 'bar', 'battery_low', 'last_update']
UVI = [432, 851, 1210, 1570, 2017, 2761, 3100, 3512, 3918, 4277, 4650, 5029,
       5230]


def main():
    try:
        s = Serial('COM3', 9600, timeout=60)

        log.debug("Connected to serial")

        while True:
            log.debug("Start Read")

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

            payload = {
                    'wind_direction': WD,
                    'humidity': HM,
                    'temperature' : TP,
                    'wind_speed' : WS,
                    'wind_gusts' : WG,
                    'rain' : RN,
                    'uvi' : UV,
                    'light' : LT,
                    'battery' : BT,
                    'pressure' : PS,
                    'last_update': int(time.time())
                }

            for k, v in payload.items():
                log.debug(k + ":" + str(v))

            log.debug("Got info")

    except AssertionError as e:
        log.error(e)

    except:
        log.exception("Exception")


if __name__ == '__main__':
    main()
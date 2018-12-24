#!/usr/bin/env python
# -*- coding: utf-8 -*-

LED_COUNT      = 50      # Number of LED pixels.
LED_PIN        = 18      # GPIO pin connected to the pixels (18 uses PWM!).
#LED_PIN        = 10      # GPIO pin connected to the pixels (10 uses SPI /dev/spidev0.0).
LED_FREQ_HZ    = 800000  # LED signal frequency in hertz (usually 800khz)
LED_DMA        = 10      # DMA channel to use for generating signal (try 10)
LED_BRIGHTNESS = 255     # Set to 0 for darkest and 255 for brightest
LED_INVERT     = False   # True to invert the signal (when using NPN transistor level shift)
LED_CHANNEL    = 0       # set to '1' for GPIOs 13, 19, 41, 45 or 53

import socket
import json
import time
from neopixel import *

UDPSock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)

listen_addr = ("",7777)
UDPSock.bind(listen_addr)
strip = Adafruit_NeoPixel(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL)
strip.begin()

for i in range(strip.numPixels()):
  strip.setPixelColor(i, Color(0,0,0))
  strip.show()
  time.sleep(50/1000.0)

while True:
  data_json,addr = UDPSock.recvfrom(10024)
  data = json.loads(data_json.strip())
  #print("-------------------------------------------------")
  for i in data:
    #print(i['i'])
    strip.setPixelColorRGB(i['i'], i['r'], i['g'], i['b'])
  strip.show()

from __future__ import print_function
from __future__ import division

import platform
import numpy as np
import config
import json

# ESP8266 uses WiFi communication
if config.DEVICE == 'esp8266':
    import socket
    _sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
# Raspberry Pi controls the LED strip directly
elif config.DEVICE == 'pi':
    import neopixel
    strip = neopixel.Adafruit_NeoPixel(config.N_PIXELS, config.LED_PIN,
                                       config.LED_FREQ_HZ, config.LED_DMA,
                                       config.LED_INVERT, config.BRIGHTNESS)
    strip.begin()

_gamma = np.load(config.GAMMA_TABLE_PATH)
"""Gamma lookup table used for nonlinear brightness correction"""

_prev_pixels = np.tile(253, (3, config.N_PIXELS))
"""Pixel values that were most recently displayed on the LED strip"""

pixels = np.tile(1, (3, config.N_PIXELS))
"""Pixel values for the LED strip"""

_is_python_2 = int(platform.python_version_tuple()[0]) == 2

def _update_esp8266():
    """Sends UDP packets to ESP8266 to update LED strip values

    The ESP8266 will receive and decode the packets to determine what values
    to display on the LED strip. The communication protocol supports LED strips
    with a maximum of 256 LEDs.

    The packet encoding scheme is:
        |i|r|g|b|
    where
        i (0 to 255): Index of LED to change (zero-based)
        r (0 to 255): Red value of LED
        g (0 to 255): Green value of LED
        b (0 to 255): Blue value of LED
    """
    global pixels, _prev_pixels
    # Truncate values and cast to integer
    pixels = np.clip(pixels, 0, 255).astype(int)
    #print(pixels)
    # Optionally apply gamma correc tio
    p = _gamma[pixels] if config.SOFTWARE_GAMMA_CORRECTION else np.copy(pixels)
    p = np.clip(p, 0, 255).astype(int)
    MAX_PIXELS_PER_PACKET = 126
    # Pixel indices
    idx = range(pixels.shape[1])
    #print(idx)
    idx = [i for i in idx if not np.array_equal(p[:, i], _prev_pixels[:, i])]
    n_packets = len(idx) // MAX_PIXELS_PER_PACKET + 1
    idx = np.array_split(idx, n_packets)
    #print(idx)
    for packet_indices in idx:
        all_data = []
        m = '' if _is_python_2 else []
        for i in packet_indices:
            if _is_python_2:
                all_data.append({'i': i, 'r': p[0][i], 'g': p[1][i], 'b': p[2][i]})
            else:
                m.append(i)  # Index of pixel to change
                m.append(p[0][i])  # Pixel red value
                m.append(p[1][i])  # Pixel green value
                m.append(p[2][i])  # Pixel blue value
        #print(all_data)
        data_json = json.dumps(all_data)
        _sock.sendto(data_json, (config.UDP_IP, config.UDP_PORT))
    _prev_pixels = np.copy(p)


def _update_pi():
    """Writes new LED values to the Raspberry Pi's LED strip

    Raspberry Pi uses the rpi_ws281x to control the LED strip directly.
    This function updates the LED strip with new values.
    """
    global pixels, _prev_pixels
    # Truncate values and cast to integer
    pixels = np.clip(pixels, 0, 255).astype(int)
    # Optional gamma correction
    p = _gamma[pixels] if config.SOFTWARE_GAMMA_CORRECTION else np.copy(pixels)
    # Encode 24-bit LED values in 32 bit integers
    r = np.left_shift(p[0][:].astype(int), 8)
    g = np.left_shift(p[1][:].astype(int), 16)
    b = p[2][:].astype(int)
    rgb = np.bitwise_or(np.bitwise_or(r, g), b)
    # Update the pixels
    for i in range(config.N_PIXELS):
        # Ignore pixels if they haven't changed (saves bandwidth)
        if np.array_equal(p[:, i], _prev_pixels[:, i]):
            continue
        strip._led_data[i] = rgb[i]
    _prev_pixels = np.copy(p)
    strip.show()


def update():
    """Updates the LED strip values"""
    if config.DEVICE == 'esp8266':
        _update_esp8266()
    elif config.DEVICE == 'pi':
        _update_pi()
    else:
        raise ValueError('Invalid device selected')


# Execute this file to run a LED strand test
# If everything is working, you should see a red, green, and blue pixel scroll
# across the LED strip continously
if __name__ == '__main__':
    import time
    # Turn all pixels off
    pixels *= 0

    for i_2 in xrange(0,5):
        for i in xrange(0,3):
            pixels[i, i_2] = 255

    for i_2 in xrange(20,25):
        for i in xrange(0,3):
            pixels[i, i_2] = 255

    print('Starting LED effects')
    while True:
        pixels = np.roll(pixels, 1, axis=1)
        update()
        time.sleep(.05)

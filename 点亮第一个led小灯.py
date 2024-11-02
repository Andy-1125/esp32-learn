from machine import Pin
import time


def liangdeng(pin_number=2, delay=0.5):
    pin = Pin(pin_number, Pin.OUT)
    while True:
        pin.value(1)
        time.sleep(delay)
        pin.value(0)
        time.sleep(delay)


if __name__ == '__main__':
    liangdeng()
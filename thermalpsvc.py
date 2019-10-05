from thermalprinter import ThermalPrinter
import RPi.GPIO as GPIO
from time import sleep
from threading import Thread
from redditdigest import get_cat_post
from datetime import datetime


LED_PIN = 18
BUTTON_PIN = 23
PRINTER_PORT = "/dev/serial0"


def get_day_section(hour):
    if 4 < hour <= 11:
        day_section = "morning"
    elif 11 < hour <= 5:
        day_section = "afternoon"
    else:
        day_section = "evening"


class PrintSvc:
    def __init__(self, port, led_pin, button_pin):
        # Printer setup
        self.printer = ThermalPrinter(port=port)
        # GPIO setup
        self.led_pin = led_pin
        self.button_pin = button_pin
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.led_pin, GPIO.OUT)
        GPIO.setup(self.button_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        print("Setup OK")

    def _set_led(self, val):
        GPIO.output(self.led_pin, val)

    def run(self):
        GPIO.remove_event_detect(self.button_pin)
        GPIO.add_event_detect(self.button_pin, GPIO.FALLING, bouncetime=200)
        GPIO.add_event_callback(self.button_pin, self._print_handler)
        while True:
            sleep(0.01)

    def _scaled_image(self, image):
        size = (384, 256)
        image.thumbnail(size)
        return image

    def _print_handler(self, pin):
        print("Button press received")
        Thread(target=self._print_message).start()

    def _print_message(self):
        self._set_led(True)
        try:
            post = get_cat_post()
            now_dt = datetime.now()
            day_section = get_day_section(now_dt.hour)
            self.printer.out("Hello! Here's a picture of a cat...")
            self.printer.image(self._scaled_image(post["pic"]))
            self.printer.out(post["title"])
            self.printer.out(post["url"])
            self.printer.out(f"Have a good {day_section}.")
        finally:
            self._set_led(False)



def main():
    printsvc = PrintSvc(port=PRINTER_PORT, led_pin=LED_PIN, button_pin=BUTTON_PIN)
    printsvc.run()


if __name__ == '__main__':
    main()

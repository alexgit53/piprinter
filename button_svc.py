import RPi.GPIO as GPIO
import redis
import logging
import time


LED_PIN = 18
BUTTON_PIN = 23
LED_KEY = "printing"
PRINT_KEY = "print"
REDIS_TRUE = "true"


class ButtonHandler:
    def __init__(self, button_pin, led_pin, redis_con, press_key, led_key):
        self.led_pin = led_pin
        self.button_pin = button_pin
        self.redis = redis_con
        self.press_key = press_key
        self.led_key = led_key
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.led_pin, GPIO.OUT)
        GPIO.setup(self.button_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        logging.info("Button setup OK")

    def run(self):
        GPIO.remove_event_detect(self.button_pin)
        GPIO.add_event_detect(self.button_pin, GPIO.FALLING, bouncetime=500)
        GPIO.add_event_callback(self.button_pin, self._button_handler)
        try:
            while True:
                if self.redis.get(self.led_key):
                    GPIO.output(self.led_pin, True)
                else:
                    GPIO.output(self.led_pin, False)
                time.sleep(0.5)
        finally:
            GPIO.output(self.led_pin, False)
            GPIO.cleanup()

    def _button_handler(self, pin):
        logging.debug("Button press received")
        self.redis.set(PRINT_KEY, REDIS_TRUE)


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    redis_con = redis.Redis(host="localhost", port=6379, db=0)
    bh = ButtonHandler(BUTTON_PIN, LED_PIN, redis_con, PRINT_KEY, LED_KEY)
    bh.run()

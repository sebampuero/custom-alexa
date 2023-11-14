import RPi.GPIO as GPIO

class LedManager():

    READY_TO_TALK_PIN = 27
    DID_NOT_UNDERSTAND_PIN = 4

    def _setup_led(self, ledpin) -> None:
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(ledpin, GPIO.OUT)

    def start_led(self, ledpin) -> None:
        self._setup_led(ledpin)
        GPIO.output(ledpin, GPIO.HIGH)


    def stop_led(self, ledpin) -> None:
        self._setup_led(ledpin)
        GPIO.output(ledpin, GPIO.LOW)
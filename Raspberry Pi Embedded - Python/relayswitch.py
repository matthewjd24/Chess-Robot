from gpiozero import LED
from time import sleep

relay = LED(17)  # Replace 17 with the GPIO pin number for your relay

while True:
    relay.on()  # Close the relay (turn on)
    print("Relay ON")
    sleep(1)
    relay.off()  # Open the relay (turn off)
    print("Relay OFF")
    sleep(1)

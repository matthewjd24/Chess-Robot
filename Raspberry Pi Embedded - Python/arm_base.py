import threading
import time
import busio
import board
from adafruit_pca9685 import PCA9685
from adafruit_motor import servo
from gpiozero import OutputDevice
from time import sleep

# Initialize I2C bus
i2c = busio.I2C(board.SCL, board.SDA)

# Initialize PCA9685
pca = PCA9685(i2c)
pca.frequency = 50  # Standard servo frequency
relay = OutputDevice(23, active_high=True, initial_value=False)

class Servo:
    def __init__(self, channel, start_angle=0):
        self.servo = servo.Servo(pca.channels[channel])
        self.current_angle = start_angle
        self.lock = threading.Lock()
        self.thread = None
        self.set_angle(start_angle)

    def set_angle(self, angle):
        """
        Set the servo to a specific angle (0-180).
        """
        with self.lock:
            self.servo.angle = angle
            self.current_angle = angle

    def move_to_angle(self, target_angle, total_time=2.0, step_count=50):
        """
        Smoothly moves the servo to the target angle over the specified time.
        """
        target_angle = max(0, min(180, target_angle))
        delay = total_time / step_count
        step = (target_angle - self.current_angle) / step_count

        def smooth_move():
            for _ in range(step_count):
                with self.lock:
                    self.current_angle += step
                    self.servo.angle = self.current_angle
                time.sleep(delay)
            with self.lock:
                self.current_angle = target_angle
                self.servo.angle = target_angle

        self.thread = threading.Thread(target=smooth_move)
        self.thread.start()

    def wait_until_done(self):
        if self.thread is not None:
            self.thread.join()

# Example Usage
if __name__ == "__main__":
    servo1 = Servo(channel=0, start_angle=90)
    print("Relay ON")
    relay.on()

    try:
        servo1.move_to_angle(0)
        servo1.wait_until_done()

        servo1.move_to_angle(180)
        servo1.wait_until_done()
    finally:
        pca.deinit()

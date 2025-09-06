import smbus2
import time

class servo_controller:
    def __init__(self, i2c_bus=1, address=0x40, channel=0):
        self.bus = smbus2.SMBus(i2c_bus)
        self.address = address
        self.channel = channel
        self.is_open = False

        self._write8(0x00, 0x00)  # MODE1
        self.set_pwm_freq(50)

    def _write8(self, reg, value):
        self.bus.write_byte_data(self.address, reg, value)

    def set_pwm_freq(self, freq_hz):
        prescaleval = 25000000.0 / 4096.0 / freq_hz - 1
        prescale = int(prescaleval + 0.5)

        oldmode = self.bus.read_byte_data(self.address, 0x00)
        newmode = (oldmode & 0x7F) | 0x10
        self._write8(0x00, newmode)
        self._write8(0xFE, prescale)
        self._write8(0x00, oldmode)
        time.sleep(0.005)
        self._write8(0x00, oldmode | 0xa1)

    def set_pwm(self, on, off):
        base = 0x06 + 4 * self.channel
        self._write8(base + 0, on & 0xFF)
        self._write8(base + 1, on >> 8)
        self._write8(base + 2, off & 0xFF)
        self._write8(base + 3, off >> 8)

    def angle_to_counts(self, angle):
        angle = max(0, min(180, angle))  # Clamp to [0, 180]
        pulse_min = 1000  # in microseconds
        pulse_max = 2000
        pulse = pulse_min + (angle / 180.0) * (pulse_max - pulse_min)
        return int(pulse / (1000000 / 50 / 4096))

    def open(self):
        if self.is_open:
            return
        counts = self.angle_to_counts(20)  # adjust angle if needed
        self.set_pwm(0, counts)
        self.is_open = True

    def close(self):
        if not self.is_open:
            return
        self.is_open = False
        self.set_pwm(0, 0)  # Stop signal = off


    def stop(self):
        # Set full-off bit to disable output on the channel
        base = 0x06 + 4 * self.channel
        self._write8(base + 3, 0x10)  # Set full OFF bit (bit 4 of LEDn_OFF_H)
        self.bus.close()


    def get_is_open(self):
        return self.is_open

    def __del__(self):
        try:
            self.stop()
        except:
            pass

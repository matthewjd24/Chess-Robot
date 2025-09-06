from dynamixel_sdk import *  # Import the Dynamixel SDK library
import time

class DxlServo:
    ADDR_POSITION_P_GAIN = 84  # Address for P gain
    ADDR_POSITION_I_GAIN = 82  # Address for I gain
    ADDR_POSITION_D_GAIN = 80  # Address for D gain
    ADDR_PROFILE_VELOCITY = 112  # Address for Profile Velocity
    ADDR_PROFILE_ACCELERATION = 108  # Address for Profile Acceleration
    ADDR_GOAL_VELOCITY = 104  # Address for velocity control
    ADDR_OPERATING_MODE = 11  # Address for setting Operating Mode
    ADDR_GOAL_POSITION = 116  # Control table address for goal position
    ADDR_PRESENT_POSITION = 132  # Control table address for present position
    ADDR_TORQUE_ENABLE = 64  # Address for enabling torque
    OPERATING_MODE_TORQUE = 0     # Current Control Mode
    OPERATING_MODE_VELOCITY = 1
    OPERATING_MODE_POSITION = 3
    TORQUE_ENABLE = 1
    TORQUE_DISABLE = 0
    ADDR_GOAL_PWM = 100
    ADDR_PRESENT_PWM = 124

    def __init__(self, dxl_id, offset, speeds, multiplier=1, operating_mode=1):
        self.PORT_NAME = '/dev/ttyUSB0'
        self.BAUD_RATE = 57600
        self.PROTOCOL_VERSION = 2.0
        self.DXL_ID = dxl_id
        self.operating_mode = operating_mode
        self.offset = offset
        self.multiplier = multiplier
        self.MIN_POSITION = 0  # Min position value (0 degrees)
        self.MAX_POSITION = 4095  # Max position value (360 degrees)
        self.offset_center = offset * 4095 / 360.0
        #print("Offset center is: " + str(self.offset_center))
        self.speeds = speeds
        self.last_set_torque = None

        # Create Port and Packet Handlers
        self.port_handler = PortHandler(self.PORT_NAME)
        self.packet_handler = PacketHandler(self.PROTOCOL_VERSION)

        # Initialize the port
        self.initialize()
        self.disable_torque()
        self.packet_handler.write1ByteTxRx(self.port_handler, self.DXL_ID, self.ADDR_OPERATING_MODE, self.operating_mode)
        self.enable_torque()
        #self.set_velocity_and_acceleration(50, 10)

    def initialize(self):
        """Initializes the communication port."""
        if not self.port_handler.openPort():
            raise Exception("Failed to open the port.")
        if not self.port_handler.setBaudRate(self.BAUD_RATE):
            raise Exception("Failed to set baudrate.")
        #print("Port initialized successfully.")

    def torque_mode(self):
        self.disable_torque()
        dxl_comm_result, dxl_error = self.packet_handler.write1ByteTxRx(self.port_handler, self.DXL_ID, self.ADDR_OPERATING_MODE, 16)
        if dxl_comm_result != COMM_SUCCESS:
            print(f"Failed to set Current Control Mode: {self.packet_handler.getTxRxResult(dxl_comm_result)}")
            return False
        elif dxl_error:
            print(f"Error setting mode: {self.packet_handler.getRxPacketError(dxl_error)}")
        self.enable_torque()

    def set_torque(self, torque):
        if torque == self.last_set_torque:
            return
        torque_constant = 1.78 # Nm/A
        current = torque / torque_constant
        dyna_units = int(current / .00269) 
        print(f"Set torque {torque:.2f} ({dyna_units} in dxl units)")
        self.last_set_torque = torque
        dxl_comm_result, dxl_error = self.packet_handler.write2ByteTxRx(self.port_handler, self.DXL_ID, 102, dyna_units)
        if dxl_comm_result != COMM_SUCCESS:
            print(f"Failed to set goal PWM: {self.packet_handler.getTxRxResult(dxl_comm_result)}")
        elif dxl_error:
            print(f"Error setting goal PWM: {self.packet_handler.getRxPacketError(dxl_error)}")

    def set_pid_gains(self, p_gain, i_gain, d_gain):
        """Sets the PID gains for the servo."""
        # Set P Gain
        dxl_comm_result, dxl_error = self.packet_handler.write2ByteTxRx(
            self.port_handler, self.DXL_ID, self.ADDR_POSITION_P_GAIN, p_gain
        )
        if dxl_comm_result != COMM_SUCCESS:
            raise Exception(f"P Gain Error: {self.packet_handler.getTxRxResult(dxl_comm_result)}")
        if dxl_error != 0:
            raise Exception(f"P Gain Error: {self.packet_handler.getRxPacketError(dxl_error)}")
        print(f"P Gain set to {p_gain}.")

        # Set I Gain
        dxl_comm_result, dxl_error = self.packet_handler.write2ByteTxRx(
            self.port_handler, self.DXL_ID, self.ADDR_POSITION_I_GAIN, i_gain
        )
        if dxl_comm_result != COMM_SUCCESS:
            raise Exception(f"I Gain Error: {self.packet_handler.getTxRxResult(dxl_comm_result)}")
        if dxl_error != 0:
            raise Exception(f"I Gain Error: {self.packet_handler.getRxPacketError(dxl_error)}")
        print(f"I Gain set to {i_gain}.")

        # Set D Gain
        dxl_comm_result, dxl_error = self.packet_handler.write2ByteTxRx(
            self.port_handler, self.DXL_ID, self.ADDR_POSITION_D_GAIN, d_gain
        )
        if dxl_comm_result != COMM_SUCCESS:
            raise Exception(f"D Gain Error: {self.packet_handler.getTxRxResult(dxl_comm_result)}")
        if dxl_error != 0:
            raise Exception(f"D Gain Error: {self.packet_handler.getRxPacketError(dxl_error)}")
        print(f"D Gain set to {d_gain}.")

    def enable_torque(self):
        """Enables torque on the servo."""
        self.packet_handler.write1ByteTxRx(self.port_handler, self.DXL_ID, self.ADDR_TORQUE_ENABLE, self.TORQUE_ENABLE)

    def disable_torque(self):
        """Disables torque on the servo."""
        self.packet_handler.write1ByteTxRx(self.port_handler, self.DXL_ID, self.ADDR_TORQUE_ENABLE, self.TORQUE_DISABLE)

    def get_present_position(self):
        """Reads and returns the present position of the servo."""
        present_position, _, _ = self.packet_handler.read4ByteTxRx(self.port_handler, self.DXL_ID, self.ADDR_PRESENT_POSITION)
        if present_position > 2**31:
            present_position = self.MAX_POSITION + present_position - 2**32
        #print("Curr position: " + str(present_position))
        if present_position > 4095:
            present_position = present_position - 4095
        return present_position
    
    def get_present_position_degrees(self):
        """Reads and returns the present position of the servo."""
        present_position = self.get_present_position()
        return self.convert_servo_position_to_degrees(present_position)

    def set_velocity_and_acceleration(self, velocity, acceleration):
        """Sets the profile velocity and acceleration for smooth movement."""
        self.packet_handler.write4ByteTxRx(self.port_handler, self.DXL_ID, self.ADDR_PROFILE_VELOCITY, velocity)
        self.packet_handler.write4ByteTxRx(self.port_handler, self.DXL_ID, self.ADDR_PROFILE_ACCELERATION, acceleration)
        print(f"Profile Velocity set to {velocity}, Acceleration set to {acceleration}.")
    
    def move_to_with_velocity(self, goal_position):
        """Moves the servo smoothly to the target using velocity control with velocity ramping."""
        stop_threshold = 10

        goal_position = self.convert_degrees_to_servo_position(goal_position)

        # Switch to velocity mode
        # self.disable_torque()
        # self.packet_handler.write1ByteTxRx(self.port_handler, self.DXL_ID, self.ADDR_OPERATING_MODE, self.OPERATING_MODE_VELOCITY)
        # self.enable_torque()

        print(f"Moving servo {self.DXL_ID} to {goal_position} with velocity control.")

        while True:
            present_position = self.get_present_position()
            raw_diff = goal_position - present_position

            # Wrap the difference so it falls within [-2048, 2047]
            if raw_diff > self.MAX_POSITION // 2:
                raw_diff -= self.MAX_POSITION
            elif raw_diff < -(self.MAX_POSITION // 2):
                raw_diff += self.MAX_POSITION

            error = abs(raw_diff)

            new_velocity = self.speeds[0]
            if error < 100:
                new_velocity = self.speeds[2]
            elif error < 250:
                new_velocity = self.speeds[1]

            if raw_diff < 0:
                new_velocity = new_velocity * -1

            # Stop if within final threshold
            if error < stop_threshold:
                break

            # Write velocity command
            self.packet_handler.write4ByteTxRx(self.port_handler, self.DXL_ID, self.ADDR_GOAL_VELOCITY, new_velocity)

            print(f"Moving... Current Position: {present_position}, Target: {goal_position}, Error: {error}, Velocity: {new_velocity}")
            time.sleep(0.1)

        # Stop movement immediately (no gradual deceleration)
        self.packet_handler.write4ByteTxRx(self.port_handler, self.DXL_ID, self.ADDR_GOAL_VELOCITY, 0)
        print(f"Now at {self.get_present_position()}, stopping.")

        # Switch back to position mode
        # self.disable_torque()
        # self.packet_handler.write1ByteTxRx(self.port_handler, self.DXL_ID, self.ADDR_OPERATING_MODE, self.OPERATING_MODE_POSITION)
        # self.enable_torque()

    def convert_servo_position_to_degrees(self, servo_position):
        """Converts the servo's internal position scale back to degrees."""
        #print("offset center: " + str(self.offset_center))
        servo_values_per_degree = self.MAX_POSITION / 360.0
        #print("multiplier: " + str(self.multiplier))
        #print("numer: " + str(servo_position - self.offset_center))
        #print("denom: " + str(servo_values_per_degree * self.multiplier))
        #difference = servo_position - self.offset_center

        result = (servo_position - self.offset_center) / (servo_values_per_degree * self.multiplier)
        if result > 180.0:
            result = result - 360.0
        return round(result, 2)
    
    def set_position(self, pos_deg, velocity=None):
        if self.operating_mode != self.OPERATING_MODE_POSITION:
            raise RuntimeError("Servo is not in position control mode.")
        
        if velocity is not None:
            velocity = int(velocity)
            self.packet_handler.write4ByteTxRx(
                self.port_handler, self.DXL_ID, self.ADDR_PROFILE_VELOCITY, velocity
            )

        self.packet_handler.write4ByteTxRx(
            self.port_handler, self.DXL_ID, self.ADDR_PROFILE_ACCELERATION, 50
        )

        goal_position = self.convert_degrees_to_servo_position(pos_deg)
        dxl_comm_result, dxl_error = self.packet_handler.write4ByteTxRx(
            self.port_handler, self.DXL_ID, self.ADDR_GOAL_POSITION, goal_position
        )

        if dxl_comm_result != COMM_SUCCESS:
            raise Exception(f"Failed to set goal position: {self.packet_handler.getTxRxResult(dxl_comm_result)}")
        if dxl_error != 0:
            raise Exception(f"Error from servo: {self.packet_handler.getRxPacketError(dxl_error)}")


    def close(self):
        """Closes the communication port."""
        self.port_handler.closePort()
        print("Port closed.")

    def convert_degrees_to_servo_position(self, pos):
        """Converts degrees to the servo's internal position scale."""
        servo_values_per_degree = self.MAX_POSITION / 360.0
        result = int(self.offset_center + (pos * servo_values_per_degree) * self.multiplier)
        if result < 0:
            result = result + self.MAX_POSITION
        return result

# Example Usage
if __name__ == "__main__":
    servo = DxlServo(1, 0)  # Initialize servo with ID 1

    print("Moving using position control:")
    servo.move_to_degrees(0)
    time.sleep(2)
    servo.move_to_degrees(-90)
    time.sleep(2)
    servo.move_to_degrees(90)

    print("Moving using velocity control:")
    servo.move_to_with_velocity(0, max_velocity=40, stop_threshold=10)
    time.sleep(2)
    servo.move_to_with_velocity(-90, max_velocity=40, stop_threshold=10)
    time.sleep(2)
    servo.move_to_with_velocity(90, max_velocity=40, stop_threshold=10)

    servo.close()

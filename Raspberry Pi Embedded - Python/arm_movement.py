import position_math
import dynamixel
import threading
import time
import math

tiles = None
base_servo = None
shoulder_servo = None
elbow_servo = None
wrist_servo = None

def initialize_tiles():
    global tiles
    tiles = position_math.get_tile_positions()

def initialize_servos():
    global base_servo, shoulder_servo, elbow_servo, wrist_servo
    base_servo = dynamixel.DxlServo(1, 257, [40, 20, 7], -1, 3)
    # base_servo.set_pid_gains(500, 40, 0)
    shoulder_servo = dynamixel.DxlServo(2, 175, [30, 12, 6], 1, 3)
    # shoulder_servo.set_pid_gains(600, 20, 0)
    elbow_servo = dynamixel.DxlServo(3, 45, [80, 12, 6], 1, 3)
    # elbow_servo.set_pid_gains(700, 20, 0)
    wrist_servo = dynamixel.DxlServo(4, 227, [80, 12, 6], 1, 3)
    # elbow_servo.set_pid_gains(800, 20, 0)

def move_arm_to_position(col, row, z_height):
    z_height = float(z_height)
    tile = tiles[col][row]
    angle = position_math.get_base_angle(tile)
    print("Target angle is " + str(angle))
    distance = position_math.get_distance_to_tile(tile)
    shoulder_angle, elbow_angle = position_math.get_elbow_shoulder_angles(distance, z_height)

    base_servo.enable_torque()
    shoulder_servo.enable_torque()
    elbow_servo.enable_torque()
    goal1 = base_servo.convert_degrees_to_servo_position(angle)
    goal2 = shoulder_servo.convert_degrees_to_servo_position(shoulder_angle)
    goal3 = elbow_servo.convert_degrees_to_servo_position(elbow_angle)

    while True:
        pos1 = base_servo.get_present_position()
        rawDiff1 = get_raw_diff(base_servo, pos1, goal1)
        error1 = abs(rawDiff1)

        pos2 = shoulder_servo.get_present_position()
        rawDiff2 = get_raw_diff(shoulder_servo, pos2, goal2)
        error2 = abs(rawDiff2)

        pos3 = elbow_servo.get_present_position()
        rawDiff3 = get_raw_diff(elbow_servo, pos3, goal3)
        error3 = abs(rawDiff3)

        print(f"Current/Target: {pos1}/{goal1}, {pos2}/{goal2}, {pos3}/{goal3}")

        if error1 <= 15 and error2 <= 15 and error3 <= 15:
            break

        set_velocity(base_servo, rawDiff1)
        set_velocity(shoulder_servo, rawDiff2)
        set_velocity(elbow_servo, rawDiff3)
        #get_velocity(elbow_servo, goal3, pos3, rawDiff3)

        ADDR_HARDWARE_ERROR_STATUS = 70
        error_status, _, _ = elbow_servo.packet_handler.read1ByteTxRx(elbow_servo.port_handler, elbow_servo.DXL_ID, ADDR_HARDWARE_ERROR_STATUS)
        if error_status != 0:
            print(f"Error Status: {error_status}")

        
        time.sleep(0.1)
    
    base_servo.packet_handler.write4ByteTxRx(base_servo.port_handler, base_servo.DXL_ID, base_servo.ADDR_GOAL_VELOCITY, 0)
    shoulder_servo.packet_handler.write4ByteTxRx(shoulder_servo.port_handler, shoulder_servo.DXL_ID, shoulder_servo.ADDR_GOAL_VELOCITY, 0)
    elbow_servo.packet_handler.write4ByteTxRx(elbow_servo.port_handler, elbow_servo.DXL_ID, elbow_servo.ADDR_GOAL_VELOCITY, 0)
    print(f"Stopped. Base: {base_servo.get_present_position()}. Shoulder: {shoulder_servo.get_present_position()}")
    print("Finished")

def move_arm_to_vector3(x, y, z):
    base_servo.enable_torque()
    shoulder_servo.enable_torque()
    elbow_servo.enable_torque()

    x = float(x)
    y = float(y)
    z = float(z)

def get_current_vector3():
    link_length = 10.0
    # Convert angles from degrees to radians
    shoulder_deg = shoulder_servo.get_present_position_degrees()
    shoulder_rad = math.radians(shoulder_deg)
    elbow_deg = elbow_servo.get_present_position_degrees()
    elbow_rad = math.radians(elbow_deg)
    
    # Compute the position of the elbow
    y1 = 9.8 * math.cos(shoulder_rad)
    x1 = 9.8 * math.sin(shoulder_rad)

    print(f"Angle: {shoulder_deg:.2f}")
    print(f"Elbow: {x1:.2f}, {y1:.2f}")

    # Total angle to the wrist (shoulder + wrist)
    total_angle = shoulder_rad + elbow_rad

    # Compute the position of the end effector
    y2 = y1 + link_length * math.cos(total_angle)
    x2 = x1 + link_length * math.sin(total_angle)

    return (x2, y2)

def get_raw_diff(servo, present_position, goal_position):
    raw_diff = goal_position - present_position

    # Wrap the difference so it falls within [-2048, 2047]
    if raw_diff > servo.MAX_POSITION // 2:
        raw_diff -= servo.MAX_POSITION
    elif raw_diff < -(servo.MAX_POSITION // 2):
        raw_diff += servo.MAX_POSITION
    return raw_diff

def set_velocity(servo, raw_diff):
    """Moves the servo smoothly to the target using velocity control with velocity ramping."""
    error = abs(raw_diff)

    new_velocity = servo.speeds[0]
    if error <= 15:
        new_velocity = 0
    elif error < 100:
        new_velocity = servo.speeds[2]
    elif error < 250:
        new_velocity = servo.speeds[1]

    if raw_diff < 0:
        new_velocity = new_velocity * -1

    #print(f"Moving servo {servo.DXL_ID}. Current Pos: {present_position}, Target: {goal_position}, Error: {error}, Velocity: {new_velocity}")
    servo.packet_handler.write4ByteTxRx(servo.port_handler, servo.DXL_ID, servo.ADDR_GOAL_VELOCITY, new_velocity)


def move_servo_to_pos():
    #distance = position_math.get_distance_to_tile(tile)
    #thread1 = threading.Thread(target=base_servo.move_to_with_velocity, args=(angle,))
    # thread2 = threading.Thread(target=shoulder_servo.move_to_with_velocity, args=(0,))
    # thread1.start()
    # time.sleep(0.1)
    # thread2.start()
    # thread1.join()
    # thread2.join()
    elbow_servo.enable_torque()
    goal1 = elbow_servo.convert_degrees_to_servo_position(0)
    while True:
        pos1 = elbow_servo.get_present_position()
        rawDiff1 = get_raw_diff(elbow_servo, pos1, goal1)
        error1 = abs(rawDiff1)
        print("Pos " + str(pos1))

        if error1 <= 15:
            break

        set_velocity(elbow_servo, rawDiff1)
        #get_velocity(elbow_servo, goal3, pos3, rawDiff3)

        ADDR_HARDWARE_ERROR_STATUS = 70
        error_status, _, _ = elbow_servo.packet_handler.read1ByteTxRx(elbow_servo.port_handler, elbow_servo.DXL_ID, ADDR_HARDWARE_ERROR_STATUS)
        print(f"Error Status: {error_status}")

        
        time.sleep(0.1)
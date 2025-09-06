import cv2
import numpy as np
import camera
import color_analyzer
import time
import button
import arm_movement
import mqtt
import sys
import signal
import servo_control

#   scp -r C:\Users\USER\Documents\GitHub\Chess-Robot\*.py matt@10.0.0.148:/home/matt/Chess-Robot
#   scp -r C:\Users\matt\Documents\GitHub\Chess-Robot\*.py matt@10.0.0.188:/home/matt/Chess-Robot

logging = False
def displayImage(img, title='Image'):
    cv2.imshow(title, img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

def split_to_64(warped_image):
    height, width, _ = warped_image.shape
    rows = 8
    cols = 8
    cell_height = height // rows
    cell_width = width // cols

    # Initialize an empty list to store the images of the cells
    cell_images = []

    for i in range(rows):
        for j in range(cols):
            # Calculate the coordinates of the current part
            x_start = j * cell_width
            y_start = i * cell_height
            x_end = (j + 1) * cell_width
            y_end = (i + 1) * cell_height

            # Extract the current part of the image
            cell = warped_image[y_start:y_end, x_start:x_end]

            # Append the extracted cell image to the list
            cell_images.append(cell)

    # Return the list of cell images
    return cell_images

def initialize_board(chessboard):
    for i in range(9):
        for x in range(9):
            chessboard[i][x] = ""
    chessboard[1][7] = "bp"
    chessboard[2][7] = "bp"
    chessboard[3][7] = "bp"
    chessboard[4][7] = "bp"
    chessboard[5][7] = "bp"
    chessboard[6][7] = "bp"
    chessboard[7][7] = "bp"
    chessboard[8][7] = "bp"

    chessboard[1][8] = "br"
    chessboard[2][8] = "bn"
    chessboard[3][8] = "bb"
    chessboard[4][8] = "bq"
    chessboard[5][8] = "bk"
    chessboard[6][8] = "bb"
    chessboard[7][8] = "bn"
    chessboard[8][8] = "br"

    
    chessboard[1][2] = "wp"
    chessboard[2][2] = "wp"
    chessboard[3][2] = "wp"
    chessboard[4][2] = "wp"
    chessboard[5][2] = "wp"
    chessboard[6][2] = "wp"
    chessboard[7][2] = "wp"
    chessboard[8][2] = "wp"

    chessboard[1][1] = "wr"
    chessboard[2][1] = "wn"
    chessboard[3][1] = "wb"
    chessboard[4][1] = "wq"
    chessboard[5][1] = "wk"
    chessboard[6][1] = "wb"
    chessboard[7][1] = "wn"
    chessboard[8][1] = "wr"

def print_chessboard(board):
    print("   a  b  c  d  e  f  g  h")  # Column labels
    print(" +-----------------------+")
    for row in range(8, 0, -1):  # Start from 8 to 1 for rows
        print(f"{row}|", end=" ")  # Print row number
        for col in range(1, 9):  # Iterate through columns 1 to 8
            piece = board[col][row] if board[col][row] != "" else "  "  # Access by [column][row]
            print(f"{piece}", end=" ")
        print(f"|{row}")  # End row with row number
    print(" +-----------------------+")
    print("   a  b  c  d  e  f  g  h")  # Column labels

def get_is_tile_light(num):
    # The row and column can be determined from the tile number
    row = num // 8  # Integer division to find the row (0 to 7)
    col = num % 8   # Modulus to find the column (0 to 7)

    # Light tiles are where the sum of row and column is even
    return (row + col) % 2 == 0

def crop_center(image, crop_percent):
    # Get the dimensions of the image (height and width)
    height, width = image.shape[:2]

    crop_size = int(width * crop_percent)

    # Ensure the image is square
    if height != width:
        raise ValueError("The image is not square!")

    # Calculate the starting and ending coordinates for cropping
    start_x = (width - crop_size) // 2
    start_y = (height - crop_size) // 2
    end_x = start_x + crop_size
    end_y = start_y + crop_size

    # Crop the center of the image
    cropped_image = image[start_y:end_y, start_x:end_x]

    return cropped_image

def analyze_board(tiles, chessboard): 
    losing_tiles = list()
    gaining_tiles = list()
    tiles_swapped_from_black_to_white = list()
    masked_tiles = list()

    for i in range(len(tiles)):
        print(i)
        row = 8 - (i // 8)  # or row = 7 - (index // 8) + 1
        col = (i % 8) + 1
        
        color = color_analyzer.determine_tile_content(tiles[i])
        prev_value = chessboard[col][row]
        if(logging):
            print("[" + str(col) + ", " + str(row) + "]: " + color + ", prev value: " + prev_value)
        if(color == "empty" and len(prev_value) > 1):
            losing_tiles.append([col,row])
        if(color != "empty" and prev_value == ""):
            gaining_tiles.append([col, row])
    
    if(logging):
        print("analyzed all tiles")
        if(len(losing_tiles) > 1):
            print("multiple tiles lost pieces")
        elif(len(losing_tiles) == 0):
            print("no tiles lost a piece")
        else: 
            print("one tile lost a piece")
        for element in losing_tiles:
            print(element)

        if(len(gaining_tiles) > 1):
            print("multiple tiles gained pieces")
        elif(len(gaining_tiles) == 0):
            print("no tiles gained a piece")
        else: 
            print("one tile gained a piece")
        for element in gaining_tiles:
            print(element) 

    return losing_tiles, gaining_tiles, tiles_swapped_from_black_to_white

def update_chessboard(chessboard, analysis):
    losing_tiles = analysis[0]
    gaining_tiles = analysis[1]
    tiles_swapped_from_black_to_white = analysis[2]

    if(len(losing_tiles) == 1 and len(gaining_tiles) == 1):
        # move piece to new tile
        newcol = gaining_tiles[0][0]
        newrow = gaining_tiles[0][1]
        oldcol = losing_tiles[0][0]
        oldrow = losing_tiles[0][1]
        chessboard[newcol][newrow] = chessboard[oldcol][oldrow]
        chessboard[oldcol][oldrow] = ""
        print("\n")
        print_chessboard(chessboard)
    elif(len(losing_tiles) == 2 and len(gaining_tiles) == 2):
        # check for castling
        print("castle?")

def main():
    # cam = camera.initialize()
    # camera.take_pic(cam)
    # camera.copy_to_desktop()
    # sys.exit(0)
    
    gripper = servo_control.servo_controller()
    arm_movement.initialize_servos()

    mqtt_handler = mqtt.mqtt_handler()
    def cleanup(signum, frame):
        mqtt_handler.disconnect()
        sys.exit(0)
 
    signal.signal(signal.SIGINT, cleanup)  # Handles Ctrl+C
    signal.signal(signal.SIGTERM, cleanup)  # Handles kill command

    button_is_pressed = False

    # arm_movement.shoulder_servo.disable_torque()
    # arm_movement.base_servo.disable_torque()
    # arm_movement.elbow_servo.disable_torque()
    # arm_movement.wrist_servo.disable_torque()

    last_base_deg = None
    last_shoulder_deg = None
    last_elbow_deg = None
    last_wrist_deg = None
    while True:
        #if not mqtt_handler.waiting_for_button:
        base = arm_movement.base_servo.get_present_position()
        base_deg = arm_movement.base_servo.convert_servo_position_to_degrees(base)
        shoulder = arm_movement.shoulder_servo.get_present_position()
        shoulder_deg = arm_movement.shoulder_servo.convert_servo_position_to_degrees(shoulder)
        elbow = arm_movement.elbow_servo.get_present_position()
        elbow_deg = arm_movement.elbow_servo.convert_servo_position_to_degrees(elbow)
        wrist = arm_movement.wrist_servo.get_present_position()
        wrist_deg = arm_movement.wrist_servo.convert_servo_position_to_degrees(wrist)
        
        mqtt_handler.publish("position/base", base_deg)
        mqtt_handler.publish("position/shoulder", shoulder_deg)
        mqtt_handler.publish("position/elbow", elbow_deg)
        mqtt_handler.publish("position/wrist", wrist_deg)
        
        print(f"Base: {base_deg:.1f}. Shoulder: {shoulder_deg:.1f}. Elbow: {elbow_deg:.1f}")
        

        if mqtt_handler.base_target is not None:
            arm_movement.base_servo.set_position(mqtt_handler.base_target, mqtt_handler.base_vel)
            mqtt_handler.base_target = None
            mqtt_handler.base_vel = None
        if mqtt_handler.shoulder_target is not None:
            arm_movement.shoulder_servo.set_position(mqtt_handler.shoulder_target, mqtt_handler.shoulder_vel)
            mqtt_handler.shoulder_target = None
            mqtt_handler.shoulder_vel = None
        if mqtt_handler.elbow_target is not None:
            arm_movement.elbow_servo.set_position(mqtt_handler.elbow_target, mqtt_handler.elbow_vel)
            mqtt_handler.elbow_target = None
            mqtt_handler.elbow_vel = None
        if mqtt_handler.wrist_target is not None:
            arm_movement.wrist_servo.set_position(mqtt_handler.wrist_target, mqtt_handler.wrist_vel)
            mqtt_handler.wrist_target = None
            mqtt_handler.wrist_vel = None
        
        if mqtt_handler.gripper_open:
            gripper.open()
        else:
            gripper.close()
        
        if button.is_pressed() == True and button_is_pressed == False:
            mqtt_handler.publish("button", "pressed")
            print("Pressed")
            button_is_pressed = True
        elif button.is_pressed() == False and button_is_pressed == True:
            mqtt_handler.publish("button", "released")
            print("Released")
            button_is_pressed = False
            
        time.sleep(0.05)

    # # tile = arm_movement.tiles[4][4]
    # # dist = position_math.get_distance_to_tile(tile)
    # # ang1, ang2 = position_math.get_elbow_shoulder_angles(dist, 3)
    # # print(f"Angles: {ang1}, {ang2}")
    # exit()
        
    # game_is_going = True
    # while(game_is_going):
    #     # wait for player to press the button

    #     if useCamera:
    #         transformed_image = camera.get_image(True, cameraObj)
    #         # get pictures of each tile, analyze the pictures, and update the virtual chessboard
    #         tiles = split_to_64(transformed_image)

    #         analysis = analyze_board(tiles, chessboard)
    #         update_chessboard(chessboard, analysis)
    #     else:
    #         print("have user input move in terminal")

    #     # convert the virtual chessboard to a form Stockfish likes and get the recommended move
    #     fen = stockfishprog.board_to_fen(chessboard)
    #     print(fen)
    #     move, score = stockfishprog.stockfish_recommended_move(fen, True)
    #     print(str(move) + " - " + score)

    #     # move robot arm

    #     game_is_going = False

main()
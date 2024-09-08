import cv2
import numpy as np
import camera
import color_analyzer
import build_masked_image
import stockfishprog

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
    # chessboard[1][7] = "bp"
    # chessboard[2][7] = "bp"
    # chessboard[3][7] = "bp"
    # chessboard[4][7] = "bp"
    # chessboard[5][7] = "bp"
    # chessboard[6][7] = "bp"
    # chessboard[7][7] = "bp"
    # chessboard[8][7] = "bp"

    # chessboard[1][8] = "br"
    # chessboard[2][8] = "bn"
    # chessboard[3][8] = "bb"
    # chessboard[4][8] = "bq"
    # chessboard[5][8] = "bk"
    # chessboard[6][8] = "bb"
    # chessboard[7][8] = "bn"
    # chessboard[8][8] = "br"

    
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
 
def analyze_board(tiles, chessboard): 
    losing_tiles = list()
    gaining_tiles = list()
    tiles_swapped_from_black_to_white = list()
    masked_tiles = list()

    for i in range(len(tiles)):
        row = 8 - (i // 8)  # or row = 7 - (index // 8) + 1
        col = (i % 8) + 1
        
        color, masked_tile = color_analyzer.determine_tile_content(tiles[i])
        masked_tiles.append(masked_tile)
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
    chessboard = [[None for _ in range(9)] for _ in range(9)]
    initialize_board(chessboard)
    print_chessboard(chessboard)
        
    game_is_going = True

    while(game_is_going):
        # wait for player to press the button

        transformed_image = camera.get_image()

        # get pictures of each tile, analyze the pictures, and update the virtual chessboard
        tiles = split_to_64(transformed_image)
        analysis = analyze_board(tiles, chessboard)
        update_chessboard(chessboard, analysis)

        # convert the virtual chessboard to a form Stockfish likes and get the recommended move
        fen = stockfishprog.board_to_fen(chessboard)
        print(fen)
        move, score = stockfishprog.stockfish_recommended_move(fen)
        print(str(move) + " - " + score)

        # move robot arm

        game_is_going = False

main()
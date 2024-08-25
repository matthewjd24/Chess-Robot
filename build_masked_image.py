import cv2
import numpy as np

def build(tile_masks):
    # Assuming all tiles are the same size
    tile_height, tile_width = tile_masks[0].shape[:2]
    board_height, board_width = 8 * tile_height, 8 * tile_width

    # Create a blank canvas for the chessboard
    chessboard_image = np.zeros((board_height, board_width, 3), dtype=np.uint8)

    for i, tile_mask in enumerate(tile_masks):
        row = 8 - (i // 8)
        col = i % 8

        # Calculate the position on the canvas where this tile should be placed
        y_start = (row - 1) * tile_height
        x_start = col * tile_width

        # Debugging output
        print(f"Tile {i}: Placing at row {row}, col {col}")
        print(f"Tile {i}: Placing at position y_start={y_start}, x_start={x_start}")

        # Ensure the region is within bounds before placing the tile
        if y_start + tile_height <= board_height and x_start + tile_width <= board_width:
            chessboard_image[y_start:y_start + tile_height, x_start:x_start + tile_width] = tile_mask
        else:
            print(f"Skipping tile {i} because it would go out of bounds.")

    return chessboard_image

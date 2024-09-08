import cv2
import numpy as np

def get_image():
    
    image = cv2.imread('C:\\Projects\\board 2.jpg')
    corners = np.load('chessboard_corners.npy')

    # image3 = image.copy()
    # for corner in corners:
    #     x, y = corner.ravel()
    #     cv2.circle(image3, (int(x), int(y)), 5, (0, 0, 255), -1)
    #displayImage(image3, 'Image with Detected Corners')

    corners = corners.reshape(-1, 2)
    top_right_inner = corners[-7]
    bottom_right_inner = corners[0]
    top_left_inner = corners[-1]
    bottom_left_inner = corners[6]
    
    tile_top_x_delta = (top_right_inner[0] - top_left_inner[0]) / 6
    tile_top_y_delta = (top_right_inner[1] - top_left_inner[1]) / 6
    tile_side_x_delta = (top_left_inner[0] - bottom_left_inner[0]) / 6
    tile_side_y_delta = (bottom_left_inner[1] - top_left_inner[1]) / 6

    #image2 = image.copy()
    #cv2.circle(image2, (int(top_right_inner[0]), int(top_right_inner[1])), 5, (0, 0, 255), -1)
    ##cv2.circle(image2, (int(top_left_inner[0] - tile_top_x_delta + tile_side_x_delta - 5), int(bottom_right_inner[1] + (tile_top_y_delta + tile_side_y_delta) * 1.3)), 5, (0, 0, 255), -1)
    #displayImage(image2, 'Image with Detected Corners')

    top_left = np.array([top_left_inner[0] - tile_top_x_delta + tile_side_x_delta, top_left_inner[1] - tile_top_y_delta - tile_side_y_delta + 5])
    top_right = np.array([top_right_inner[0] + tile_top_x_delta + tile_side_x_delta - 5, top_right_inner[1] + tile_top_y_delta - tile_side_y_delta + 5])
    bottom_left = np.array([bottom_left_inner[0] - tile_top_x_delta - tile_side_x_delta - 4, bottom_left_inner[1] - tile_top_y_delta + tile_side_y_delta])
    bottom_right = np.array([bottom_right_inner[0] + tile_top_x_delta - tile_side_x_delta + 7, bottom_right_inner[1] + (tile_top_y_delta + tile_side_y_delta)])

    # image2 = image.copy()
    # cv2.circle(image2, (int(top_left[0]), int(top_left[1])), 5, (0, 0, 255), -1)
    # cv2.circle(image2, (int(top_right[0]), int(top_right[1])), 5, (0, 0, 255), -1)
    # cv2.circle(image2, (int(bottom_left[0]), int(bottom_left[1])), 5, (0, 0, 255), -1)
    # cv2.circle(image2, (int(bottom_right[0]), int(bottom_right[1])), 5, (0, 0, 255), -1)
    #displayImage(image2, 'Image with Detected Corners')

    # Source points
    src_points = np.array([top_left, top_right, bottom_left, bottom_right], dtype='float32')

    # Destination points: Define where the corners should be in the 'face up' view.
    board_size = 500  # Desired size of the output image (board will be board_size x board_size)
    dst_points = np.array([
        [0, 0],
        [board_size - 1, 0],
        [0, board_size - 1],
        [board_size - 1, board_size - 1]
    ], dtype='float32')

    # Calculate the perspective transform matrix
    M = cv2.getPerspectiveTransform(src_points, dst_points)

    # Apply the perspective transformation to the image
    warped_image = cv2.warpPerspective(image, M, (board_size, board_size))
    warped_image = cv2.flip(warped_image, -1)

    # Display the result
    #displayImage(warped_image, 'Warped Chessboard (Face Up)')
    return warped_image

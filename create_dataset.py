import cv2
import numpy as np

def displayImage(img, title='Image'):
    cv2.imshow(title, img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()



#print(corners[0][0][0])

def get_transformed_image():
    # Load the image and corners
    image_path = 'C:\\Projects\\faces.jpg'
    image = cv2.imread(image_path)
    corners = np.load('chessboard_corners.npy')
    image3 = image.copy()
    for corner in corners:
        x, y = corner.ravel()
        cv2.circle(image3, (int(x), int(y)), 5, (0, 0, 255), -1)
    displayImage(image3, 'Image with Detected Corners')

    corners = corners.reshape(-1, 2)
    top_left_inner = corners[-7]
    top_right_inner = corners[0]
    bottom_left_inner = corners[-1]
    bottom_right_inner = corners[6]

    tile_top_x_delta = (top_right_inner[0] - top_left_inner[0]) / 6
    tile_top_y_delta = (top_right_inner[1] - top_left_inner[1]) / 6
    tile_side_x_delta = (top_left_inner[0] - bottom_left_inner[0]) / 6
    tile_side_y_delta = (bottom_left_inner[1] - top_left_inner[1]) / 6

    # image2 = image.copy()
    # cv2.circle(image2, (int(bottom_right_inner[0]), int(bottom_right_inner[1])), 5, (0, 0, 255), -1)
    # cv2.circle(image2, (int(bottom_right_inner[0] + tile_top_x_delta - tile_side_x_delta - 5), int(bottom_right_inner[1] + (tile_top_y_delta + tile_side_y_delta) * 1.3)), 5, (0, 0, 255), -1)
    # displayImage(image2, 'Image with Detected Corners')


    top_left = np.array([top_left_inner[0] - tile_top_x_delta + tile_side_x_delta -2, top_left_inner[1] - tile_top_y_delta - tile_side_y_delta + 4])
    top_right = np.array([top_right_inner[0] + tile_top_x_delta + tile_side_x_delta, top_right_inner[1] + tile_top_y_delta - tile_side_y_delta])
    bottom_left = np.array([bottom_left_inner[0] - tile_top_x_delta - tile_side_x_delta, bottom_left_inner[1] - tile_top_y_delta + tile_side_y_delta])
    bottom_right = np.array([bottom_right_inner[0] + tile_top_x_delta - tile_side_x_delta - 5, bottom_right_inner[1] + (tile_top_y_delta + tile_side_y_delta)*1.3])

    image2 = image.copy()
    cv2.circle(image2, (int(top_left[0]), int(top_left[1])), 5, (0, 0, 255), -1)
    cv2.circle(image2, (int(top_right[0]), int(top_right[1])), 5, (0, 0, 255), -1)
    cv2.circle(image2, (int(bottom_left[0]), int(bottom_left[1])), 5, (0, 0, 255), -1)
    cv2.circle(image2, (int(bottom_right[0]), int(bottom_right[1])), 5, (0, 0, 255), -1)
    displayImage(image2, 'Image with Detected Corners')

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

    # Display the result
    displayImage(warped_image, 'Warped Chessboard (Face Up)')
    return warped_image


# Assuming the chessboard corners were detected in order from top-left to bottom-right,
# select the four corners corresponding to the chessboard's edges:
# You may need to select specific indices depending on your chessboard detection.




def split_to_64(warped_image):
    height, width, _ = warped_image.shape
    rows = 8
    cols = 8
    cell_height = height // rows
    cell_width = width // cols
    for i in range(rows):
        for j in range(cols):
            # Calculate the coordinates of the current part
            x_start = j * cell_width
            y_start = i * cell_height
            x_end = (j + 1) * cell_width
            y_end = (i + 1) * cell_height

            # Extract the current part of the image
            cell = warped_image[y_start:y_end, x_start:x_end]

            # Optionally, display the part or save it
            # For example, to display:
            #cv2.imshow(f'Cell ({i},{j})', cell)
            print(str(i) + ", " + str(j))
            #cv2.waitKey(100)  # Display each cell for 500 ms

            # To save each part as an image file:
            cv2.imwrite(f'cell_{i}_{j}.jpg', cell)

    cv2.destroyAllWindows()
    

warped_image = get_transformed_image()
split_to_64(warped_image)
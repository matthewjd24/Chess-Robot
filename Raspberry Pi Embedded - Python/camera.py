import cv2
import numpy as np
import time
import paramiko
from scp import SCPClient

def initialize():
    cameraObj = cv2.VideoCapture(0)
    # Check if the camera opened successfully
    if not cameraObj.isOpened():
        print("Error: Could not open camera.")
        exit()
    return cameraObj

def displayImage(img, title='Image'):
    cv2.imshow(title, img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

def undistort(image):
    h, w = image.shape[:2]
    K = np.array([[w, 0, w / 2],
                [0, h, h / 2],
                [0, 0, 1]], dtype=np.float32)
    D = np.array([-.1, -.1, 0.0, 0.0], dtype=np.float32)
    h, w = image.shape[:2]
    new_K = cv2.fisheye.estimateNewCameraMatrixForUndistortRectify(K, D, (w, h), np.eye(3), balance=1)
    map1, map2 = cv2.fisheye.initUndistortRectifyMap(K, D, np.eye(3), new_K, (w, h), cv2.CV_16SC2)
    undistorted_img = cv2.remap(image, map1, map2, interpolation=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT)
    return undistorted_img

def take_pic(camera):
    # Capture multiple frames to allow the camera to adjust
    for i in range(10):  # Capture 10 frames, discarding them
        ret, frame = camera.read()
        time.sleep(0.1)

    # Now capture the actual image
    ret, frame = camera.read()

    # Check if the frame was captured successfully
    if ret:
        # Save the captured frame as an image file
        cv2.imwrite("captured_image.jpg", frame)
        print("Image saved as captured_image.jpg")
    else:
        print("Error: Could not read frame.")

    # Release the camera
    camera.release()
    return frame

def copy_to_desktop():
    ssh = paramiko.SSHClient()
    ssh.load_system_host_keys()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    ssh.connect(hostname='10.0.0.252', port=22, username='matt', password=' ')
    
    with SCPClient(ssh.get_transport()) as scp:
        scp.put('captured_image.jpg', 'C:/Users/matt/Documents/GitHub/Chess-Robot/')

    ssh.close()

def get_image(isOnPi, camera):
    
    image = take_pic(camera)
    #displayImage(image)
    image = undistort(image)
    #displayImage(image)
    # if not isOnPi: 
    #     image = cv2.imread('board_2.jpg')
    corners = np.load('chessboard_corners.npy')

    image3 = image.copy()
    for corner in corners:
        x, y = corner.ravel()
        cv2.circle(image3, (int(x), int(y)), 5, (0, 0, 255), -1)
    #displayImage(image, 'Image with Detected Corners')

    corners = corners.reshape(-1, 2)
    top_right_inner = corners[-7]
    bottom_right_inner = corners[0]
    top_left_inner = corners[-1]
    bottom_left_inner = corners[6]
    
    tile_top_x_delta = (top_right_inner[0] - top_left_inner[0]) / 6
    tile_top_y_delta = (top_right_inner[1] - top_left_inner[1]) / 6
    tile_side_x_delta = (top_left_inner[0] - bottom_left_inner[0]) / 6
    tile_side_y_delta = (bottom_left_inner[1] - top_left_inner[1]) / 6

    # image2 = image.copy()
    # cv2.circle(image2, (int(top_right_inner[0]), int(top_right_inner[1])), 5, (0, 0, 255), -1)
    # #cv2.circle(image2, (int(top_left_inner[0] - tile_top_x_delta + tile_side_x_delta - 5), int(bottom_right_inner[1] + (tile_top_y_delta + tile_side_y_delta) * 1.3)), 5, (0, 0, 255), -1)
    # displayImage(image2, 'Image with Detected Corners')

    top_left = np.array([top_left_inner[0] - tile_top_x_delta + tile_side_x_delta + 2, top_left_inner[1] - tile_top_y_delta - tile_side_y_delta])
    top_right = np.array([top_right_inner[0] + tile_top_x_delta + tile_side_x_delta, top_right_inner[1] + tile_top_y_delta - tile_side_y_delta])
    bottom_left = np.array([bottom_left_inner[0] - tile_top_x_delta - tile_side_x_delta + 2, bottom_left_inner[1] - tile_top_y_delta + tile_side_y_delta])
    bottom_right = np.array([bottom_right_inner[0] + tile_top_x_delta - tile_side_x_delta - 4, bottom_right_inner[1] + (tile_top_y_delta + tile_side_y_delta) - 2])

    image2 = image.copy()
    cv2.circle(image2, (int(top_left[0]), int(top_left[1])), 5, (0, 0, 255), -1)
    cv2.circle(image2, (int(top_right[0]), int(top_right[1])), 5, (0, 0, 255), -1)
    cv2.circle(image2, (int(bottom_left[0]), int(bottom_left[1])), 5, (0, 0, 255), -1)
    cv2.circle(image2, (int(bottom_right[0]), int(bottom_right[1])), 5, (0, 0, 255), -1)
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
    displayImage(warped_image, 'Warped Chessboard (Face Up)')
    return warped_image

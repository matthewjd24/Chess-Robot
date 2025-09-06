import cv2
import numpy as np
import camera

def displayImage(img, title='Image'):
    cv2.imshow(title, img)
    cv2.waitKey(0)
    #scv2.destroyAllWindows()



def main():
    rawimg = cv2.imread('captured_image.jpg')
    empty_board_image = camera.undistort(rawimg)
    # Load the image of the empty chessboard
    #empty_board_image = cv2.imread('test.jpg')

    gray_empty = cv2.cvtColor(empty_board_image, cv2.COLOR_BGR2GRAY)
    displayImage(gray_empty)

    equal = cv2.equalizeHist(gray_empty)
    displayImage(equal)

    blurred_image = cv2.GaussianBlur(equal, (9, 9), 0)
    displayImage(blurred_image)

    ret, corners = cv2.findChessboardCorners(blurred_image, (7, 7), None)

    if ret:
        # Refine corner positions to subpixel accuracy
        criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)
        corners = cv2.cornerSubPix(blurred_image, corners, (11, 11), (-1, -1), criteria)

        # Draw and save the corners
        cv2.drawChessboardCorners(empty_board_image, (7, 7), corners, ret)
        displayImage(empty_board_image)
        cv2.imwrite('detected_corners.jpg', empty_board_image)
        cv2.waitKey(0)

        # Save the detected corners for later use
        np.save('chessboard_corners.npy', corners)
    else:
        print("Chessboard corners not detected.")

main()

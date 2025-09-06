import cv2
import numpy as np

def displayImage(img, title='Image'):
    cv2.imshow(title, img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

def get_average_value(image):
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    average_value = np.mean(gray_image)
    return average_value

def determine_tile_content(image):
    #image = cv2.imread('C:\\Projects\\test_tile.jpg')
    hsv_image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    threshold = 20 
    def check_if_black():
        saturation_threshold = 255 * .2  # Threshold for saturation
        value_threshold = 255 * 0.08  # Threshold for value (93% of 255)

        # Create masks for pixels above the value threshold and below the saturation threshold
        #saturation_mask = cv2.inRange(hsv_image[:, :, 1], 0, saturation_threshold)
        value_mask = cv2.inRange(hsv_image[:, :, 2], 0, value_threshold)

        # Combine the masks to find pixels that satisfy both conditions
        #combined_mask = cv2.bitwise_and(saturation_mask, value_mask)

        # Clean up the combined mask using morphological operations if needed
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
        combined_mask_cleaned = cv2.morphologyEx(value_mask, cv2.MORPH_CLOSE, kernel)

        # Count the pixels that meet both criteria
        pixel_count = np.sum(combined_mask_cleaned > 0)

        # Calculate the area of the image
        tile_height, tile_width = hsv_image.shape[:2]
        tile_area = tile_height * tile_width

        # Calculate the percentage of pixels that meet both conditions
        percent_below_value_max = (pixel_count / tile_area) * 100

        # Create an output image for visualization
        output_image = cv2.bitwise_and(cv2.cvtColor(hsv_image, cv2.COLOR_HSV2BGR), cv2.cvtColor(hsv_image, cv2.COLOR_HSV2BGR), mask=combined_mask_cleaned)
        
        color = [128, 128, 128]  # White
        output_image[combined_mask_cleaned == 0] = color


        if(percent_below_value_max > 5):
            displayImage(image)
            displayImage(output_image)
        print("Black percent: " + "{:.2f}".format(percent_below_value_max))
        
        if(percent_below_value_max > 15):
            return "black"
        return "empty"

    def check_if_white():
        saturation_threshold = 255 * .2  # Threshold for saturation
        value_threshold = 255 * 0.85  # Threshold for value (93% of 255)

        # Create masks for pixels above the value threshold and below the saturation threshold
        saturation_mask = cv2.inRange(hsv_image[:, :, 1], 0, saturation_threshold)
        value_mask = cv2.inRange(hsv_image[:, :, 2], value_threshold, 255)

        # Combine the masks to find pixels that satisfy both conditions
        combined_mask = cv2.bitwise_and(saturation_mask, value_mask)

        # Clean up the combined mask using morphological operations if needed
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
        combined_mask_cleaned = cv2.morphologyEx(combined_mask, cv2.MORPH_CLOSE, kernel)

        # Count the pixels that meet both criteria
        pixel_count = np.sum(combined_mask_cleaned > 0)

        # Calculate the area of the image
        tile_height, tile_width = hsv_image.shape[:2]
        tile_area = tile_height * tile_width

        # Calculate the percentage of pixels that meet both conditions
        percent_above_value_min = (pixel_count / tile_area) * 100

        # Create an output image for visualization
        output_image = cv2.bitwise_and(cv2.cvtColor(hsv_image, cv2.COLOR_HSV2BGR), cv2.cvtColor(hsv_image, cv2.COLOR_HSV2BGR), mask=combined_mask_cleaned)
        if(percent_above_value_min > 5):
            displayImage(image)
            displayImage(output_image)
        print("White percent: " + "{:.2f}".format(percent_above_value_min))
        
        if(percent_above_value_min > 15):
            return "white"
        return "empty"

    
    content = check_if_white()
    if(content == "empty"):
        content = check_if_black()

    if(content == "white"):
        print("WHITE!!!")
    if(content == "black"):
        print("BLACK!!!")

    return content

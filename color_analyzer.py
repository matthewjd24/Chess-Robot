import cv2
import numpy as np

def displayImage(img, title='Image'):
    cv2.imshow(title, img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

def determine_tile_content(image):
    #image = cv2.imread('C:\\Projects\\test_tile.jpg')
    hsv_image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    threshold = 20 
    def check_if_black():
        lower_black = (0, 0, 0)
        upper_black = (255, 255, 60)
        mask_black = cv2.inRange(hsv_image, lower_black, upper_black)
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
        mask_cleaned = cv2.morphologyEx(mask_black, cv2.MORPH_CLOSE, kernel)
        black_pixel_count = np.sum(mask_cleaned > 0)
        tile_height, tile_width = mask_cleaned.shape
        tile_area = tile_height * tile_width
        black_percentage = (black_pixel_count / tile_area) * 100
        if black_percentage > threshold:
            return "black"
        return "empty", None

    def check_if_white():
        saturation_threshold = 38  # Threshold for saturation
        value_threshold = 184      # Threshold for value

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

        # Calculate the percentages
        percent_above_value_threshold = (pixel_count / tile_area) * 100
        percent_below_saturation_threshold = 100 - percent_above_value_threshold
        percent_in_combined_mask = 100 * pixel_count / tile_area

        #print(f"% below S threshold: {percent_below_saturation_threshold:.2f}, % above V threshold: {percent_above_value_threshold:.2f}")
        #print("Combined: " + str(percent_in_combined_mask))

        # Create an output image where only the selected areas are visible
        output_image = cv2.bitwise_and(cv2.cvtColor(hsv_image, cv2.COLOR_HSV2BGR), cv2.cvtColor(hsv_image, cv2.COLOR_HSV2BGR), mask=combined_mask_cleaned)

        # Display the output image


        # Determine if the criteria for being "white" are met
        if percent_in_combined_mask > 17:
            
            #displayImage(image)
            #displayImage(output_image)
            return "white", output_image
        return "empty", output_image
    
    content, masked_image = check_if_black()
    if(content == "empty"):
        content, masked_image = check_if_white()

    return content, masked_image


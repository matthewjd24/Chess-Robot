import numpy as np
import matplotlib.pyplot as plt
import struct

def read_idx(filename):
    with open(filename, 'rb') as f:
        # Read the header information
        magic, num_images, rows, cols = struct.unpack(">IIII", f.read(16))
        # Read the image data
        images = np.fromfile(f, dtype=np.uint8).reshape(num_images, rows, cols)
    return images

# Load the training images
train_images = read_idx('C:\\Projects\\train-images.idx3-ubyte')

# Display the first image
plt.imshow(train_images[2], cmap='gray')
plt.show()

# To display another image, just change the index in train_images[i]

import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
import tensorflow as tf
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image
import numpy as np

# Load the trained model
model = load_model('my_model.keras')

# Load and preprocess the image
img = image.load_img('C:\\Projects\\test 7.jpg', target_size=(28, 28), color_mode='grayscale')
img_array = image.img_to_array(img)
img_array = img_array / 255.0  # Normalize to match training conditions
img_array = img_array.reshape(1, 28*28)  # Flatten the image to shape (1, 784)

# Predict the class (digit) of the image
logits = model.predict(img_array)

# Apply softmax to convert logits to probabilities
probabilities = tf.nn.softmax(logits[0]).numpy()

# Get the top 3 predicted classes and their probabilities
top_3_indices = np.argsort(probabilities)[-3:][::-1]  # Sort and get top 3 indices
top_3_probabilities = probabilities[top_3_indices]  # Get the probabilities for the top 3 classes

# Print the top 3 results
for i in range(3):
    print(f"Prediction {i+1}: Number {top_3_indices[i]} with probability {top_3_probabilities[i]:.4f}")

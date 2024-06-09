import cv2
import numpy as np
import os
import sys

import tensorflow as tf
from sklearn.model_selection import train_test_split


EPOCHS = 10
IMG_WIDTH = 30
IMG_HEIGHT = 30
NUM_CATEGORIES = 43
TEST_SIZE = 0.4


def main():

    # Check command-line arguments
    if len(sys.argv) not in [2, 3]:
        sys.exit("Usage: python traffic.py data_directory [model.h5]")

    # Get image arrays and labels for all image files
    images, labels = load_data(sys.argv[1])

    # # Split data into training and testing sets
    labels = tf.keras.utils.to_categorical(labels)
    x_train, x_test, y_train, y_test = train_test_split(
        np.array(images), np.array(labels), test_size=TEST_SIZE
    )

    # # Get a compiled neural network
    model = get_model()

    # # Fit model on training data
    model.fit(x_train, y_train, epochs=EPOCHS)

    # # Evaluate neural network performance
    model.evaluate(x_test, y_test, verbose=2)

    # Save model to file
    if len(sys.argv) == 3:
        filename = sys.argv[2]
        model.save(filename)
        print(f"Model saved to {filename}.")


def load_data(data_dir):
    """
    Load image data from directory `data_dir`.

    Assume `data_dir` has one directory named after each category, numbered
    0 through NUM_CATEGORIES - 1. Inside each category directory will be some
    number of image files.

    Return tuple `(images, labels)`. `images` should be a list of all
    of the images in the data directory, where each image is formatted as a
    numpy ndarray with dimensions IMG_WIDTH x IMG_HEIGHT x 3. `labels` should
    be a list of integer labels, representing the categories for each of the
    corresponding `images`.
    """

    # Declare an empty List for holding images and labels
    images = []
    labels = []

    # Iterate over Categories
    for category in range(NUM_CATEGORIES):
        # Form the Path of the img directory
        category_dir = os.path.join(data_dir, str(category))

        # Print a message to indicate which directory is being read currently
        print(f"Started Searching {category_dir}")

        # For each image in the directory
        for image_name in os.listdir(category_dir):

            image_path = os.path.join(category_dir, image_name)

            # Read the image using open cv
            image = cv2.imread(image_path)

            # Resize the image
            image = cv2.resize(image, (IMG_WIDTH, IMG_HEIGHT))

            # Add the image and it's category to the List
            images.append(image)
            labels.append(category)

    # Return images and labels
    return images, labels


def get_model():
    """
    Returns a compiled convolutional neural network model. Assume that the
    `input_shape` of the first layer is `(IMG_WIDTH, IMG_HEIGHT, 3)`.
    The output layer should have `NUM_CATEGORIES` units, one for each category.
    """

    # Define the sequential model
    model = tf.keras.models.Sequential(
        [
            # Convolutional layer with 32 filters of size 3x3, using ReLU activation
            tf.keras.layers.Conv2D(32, (3, 3), activation="relu"),
            # Max pooling layer with pool size 2x2
            tf.keras.layers.MaxPooling2D((2, 2)),
            # Convolutional layer with 64 filters of size 3x3, using ReLU activation
            tf.keras.layers.Conv2D(64, (3, 3), activation="relu"),
            # Max pooling layer with pool size 2x2
            tf.keras.layers.MaxPooling2D((2, 2)),
            # Convolutional layer with 128 filters of size 3x3, using ReLU activation
            tf.keras.layers.Conv2D(128, (3, 3), activation="relu"),
            # Max pooling layer with pool size 2x2
            tf.keras.layers.MaxPooling2D((2, 2)),
            # Flatten layer to convert 2D matrix data to a vector
            tf.keras.layers.Flatten(),
            # Fully connected layer with 512 units, using ReLU activation
            tf.keras.layers.Dense(512, activation="relu"),
            # Dropout layer with dropout rate of 0.5 to prevent overfitting
            tf.keras.layers.Dropout(0.5),
            # Output layer with NUM_CATEGORIES units, using softmax activation
            tf.keras.layers.Dense(NUM_CATEGORIES, activation="softmax"),
        ]
    )

    # Compile the model
    model.compile(
        optimizer="adam", loss="categorical_crossentropy", metrics=["accuracy"]
    )

    # Return the model
    return model


if __name__ == "__main__":
    main()

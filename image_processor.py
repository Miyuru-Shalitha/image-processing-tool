import cv2
import numpy as np
from enum import Enum


class ColorMode(Enum):
    RGB = 3,
    BW = 1


def change_color_mode(image_data, width, height, color_mode):
    image_array = np.frombuffer(image_data, dtype=np.uint8)
    image_array = image_array.reshape((height, width, 3))
    gray_image = cv2.cvtColor(image_array, cv2.COLOR_RGB2GRAY)

    return gray_image


def rotate_image(image_data, width, height, angle, number_of_channels):
    image_array = np.frombuffer(image_data, dtype=np.uint8)
    image_array = image_array.reshape((height, width, number_of_channels))
    center = (width / 2, height / 2)
    rotation_matrix = cv2.getRotationMatrix2D(center, angle, 1.0)
    rotated_image = cv2.warpAffine(image_array, rotation_matrix, (width, height))

    return rotated_image

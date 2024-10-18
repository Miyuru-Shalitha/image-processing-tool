import cv2
import numpy as np
import tensorflow as tf
from enum import Enum


class OperationType(Enum):
    CONVERT_TO_GRAY_SCALE = 0
    ROTATE = 1
    FLIP_VERTICALLY = 2
    FLIP_HORIZONTALLY = 3
    BOX_FILTER = 4
    GAUSSIAN_FILTER = 5
    EDGE_DETECTION = 6
    DENOISING = 7


class Operation:
    def __init__(self, entity_handle: int, texture_id: int, operation_type: OperationType) -> None:
        self.entity_handle: int = entity_handle
        self.texture_id: int = texture_id
        self.operation_type: OperationType = operation_type


def change_color_mode(image_data: bytes, width: int, height: int, number_of_channels: int):
    image_array = np.frombuffer(image_data, dtype=np.uint8)
    image_array = image_array.reshape((height, width, number_of_channels))
    gray_image = cv2.cvtColor(image_array, cv2.COLOR_RGB2GRAY)

    return gray_image


def rotate_image(image_data: bytes, width: int, height: int, angle: float, number_of_channels: int):
    image_array = np.frombuffer(image_data, dtype=np.uint8)
    image_array = image_array.reshape((height, width, number_of_channels))
    center = (width / 2, height / 2)
    rotation_matrix = cv2.getRotationMatrix2D(center, angle, 1.0)
    rotated_image = cv2.warpAffine(image_array, rotation_matrix, (width, height))

    return rotated_image


def flip_image_horizontally(image_data: bytes, width: int, height: int, number_of_channels: int):
    image_array = np.frombuffer(image_data, dtype=np.uint8)
    image_array = image_array.reshape((height, width, number_of_channels))
    flipped_image = cv2.flip(image_array, 1)

    return flipped_image


def flip_image_vertically(image_data: bytes, width: int, height: int, number_of_channels: int):
    image_array = np.frombuffer(image_data, dtype=np.uint8)
    image_array = image_array.reshape((height, width, number_of_channels))
    flipped_image = cv2.flip(image_array, 0)

    return flipped_image


def box_filter(image_data: bytes, width: int, height: int, number_of_channels: int, kernel_size: tuple[int, int]):
    image_array = np.frombuffer(image_data, dtype=np.uint8)
    image_array = image_array.reshape((height, width, number_of_channels))
    filtered_image = cv2.boxFilter(image_array, -1, kernel_size)

    return filtered_image


def gaussian_filter(image_data: bytes, width: int, height: int, number_of_channels: int, kernel_size: tuple[int, int], sigma_x: float):
    image_array = np.frombuffer(image_data, dtype=np.uint8)
    image_array = image_array.reshape((height, width, number_of_channels))
    blurred_image = cv2.GaussianBlur(image_array, kernel_size, sigma_x)

    return blurred_image


def sobel_edge_ditection(image_data: bytes, width: int, height: int, number_of_channels: int):
    image_array = np.frombuffer(image_data, dtype=np.uint8)
    image_array = image_array.reshape((height, width, number_of_channels))

    if number_of_channels == 3:
        gray_image = cv2.cvtColor(image_array, cv2.COLOR_RGB2GRAY)
    else:
        gray_image = image_array

    sobel_x = cv2.Sobel(gray_image, cv2.CV_64F, 1, 0, ksize=5)
    sobel_y = cv2.Sobel(gray_image, cv2.CV_64F, 0, 1, ksize=5)

    edges = np.sqrt(sobel_x**2 + sobel_y**2)
    edges = np.uint8(np.clip(edges, 0, 255))

    return edges


def denoise_image(image_data: bytes, width: int, height: int, number_of_channels: int):
    image_array = np.frombuffer(image_data, dtype=np.uint8)
    image_array = image_array.reshape((height, width, number_of_channels))

    image_array = image_array.astype(np.float32) / 255.0
    image_array = np.expand_dims(image_array, axis=0)
    model = tf.keras.models.load_model("models/denoising_model.h5")
    denoised_image = model.predict(image_array)

    denoised_image = np.squeeze(denoised_image)
    denoised_image = np.clip(denoised_image, 0, 1)
    denoised_image = (denoised_image * 255).astype(np.uint8)

    return denoised_image


from typing import Tuple
import cv2
import numpy as np
from enum import Enum


class OperationType(Enum):
    CONVERT_TO_GRAY_SCALE = 0
    ROTATE = 1
    FLIP_VERTICALLY = 2
    FLIP_HORIZONTALLY = 3
    BOX_FILTER = 4


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


def box_filter(image_data: bytes, width: int, height: int, number_of_channels: int, kernel_size: Tuple[int, int]):
    image_array = np.frombuffer(image_data, dtype=np.uint8)
    image_array = image_array.reshape((height, width, number_of_channels))
    filtered_image = cv2.boxFilter(image_array, -1, kernel_size)

    return filtered_image

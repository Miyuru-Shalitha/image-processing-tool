import pygame
from typing import Tuple
from OpenGL import GL


class Image:
    def __init__(self, file_path: str, name: str, data: bytes, width: int, height: int, number_of_channels: int) -> None:
        self.file_path: str = file_path
        self.name: str = name
        self.data: bytes = data
        self.width: int = width
        self.height: int = height
        self.number_of_channels: int = number_of_channels


class Texture:
    def __init__(self, id: int, name: str) -> None:
        self.id: str = id
        self.name: str = name


images: list[Image] = []
textures: list[Texture] = []


def load_image(file_path: str) -> Image:
    image_surface = pygame.image.load(file_path)
    # image_surface = pygame.transform.flip(image_surface, False, True)
    image_data: bytes = pygame.image.tostring(image_surface, "RGB", True)
    width, height = image_surface.get_size()
    image = Image(file_path, file_path.split('/')[-1], image_data, width, height, 3)
    images.append(image)

    return image


def create_texture(name: str, data: bytes, width: int, height: int, number_of_channels: int) -> Texture:
    if number_of_channels == 1:
        format = GL.GL_RED
    elif number_of_channels == 3:
        format = GL.GL_RGB
    elif number_of_channels == 4:
        format = GL.GL_RGBA
    else:
        # TODO(Miyuru): Handle error
        pass

    texture_id = GL.glGenTextures(1)
    GL.glBindTexture(GL.GL_TEXTURE_2D, texture_id)
    GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_MIN_FILTER, GL.GL_LINEAR)
    GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_MAG_FILTER, GL.GL_LINEAR)
    GL.glTexImage2D(GL.GL_TEXTURE_2D, 0, format, width, height, 0, format, GL.GL_UNSIGNED_BYTE, data)
    GL.glGenerateMipmap(GL.GL_TEXTURE_2D)

    texture = Texture(texture_id, name)
    textures.append(texture)

    return texture


def get_texture_width(texture_id: int) -> int:
    GL.glBindTexture(GL.GL_TEXTURE_2D, texture_id)
    width = GL.glGetTexLevelParameteriv(GL.GL_TEXTURE_2D, 0, GL.GL_TEXTURE_WIDTH)
    GL.glBindTexture(GL.GL_TEXTURE_2D, 0)

    return width


def get_texture_height(texture_id: int) -> int:
    GL.glBindTexture(GL.GL_TEXTURE_2D, texture_id)
    height = GL.glGetTexLevelParameteriv(GL.GL_TEXTURE_2D, 0, GL.GL_TEXTURE_HEIGHT)
    GL.glBindTexture(GL.GL_TEXTURE_2D, 0)

    return height

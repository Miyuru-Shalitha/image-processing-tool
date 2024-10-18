import pygame
import glm
from OpenGL.GL import *
from enum import Enum


class ComponentType(Enum):
    COLOR_MANIPULATOR_COMPONENT = 0,
    IMAGE_TRANSFORM_COMPONENT = 1


class Entity:
    def __init__(self, id):
        self.id = id
        self.components: list[ComponentType] = []


class ColorMode(Enum):
    COLOR_MODE_ORIGINAL = 0,
    COLOR_MODE_BW = 1


class ColorManipulationOperation:
    def __init__(self, texture_handle, previouse_mode, new_mode):
        self.texture_handle = texture_handle
        self.previouse_mode = previouse_mode
        self.new_mode = new_mode


class RotationOperation:
    def __init__(self, texture_handle):
        self.texture_handle = texture_handle


class Texture:
    def __init__(self, name, id, entity_handle, data, number_of_channels):
        self.name = name
        self.id = id
        self.entity_handle = entity_handle
        self.data = data
        self.number_of_channels = number_of_channels
        self.position = glm.vec2(0.0, 0.0)
        self.operation = None


entity_handle_accumilator = -1
entities: list[Entity] = []
textures: list[Texture] = []


def create_entity():
    global entity_handle_accumilator

    entity_handle_accumilator += 1
    return Entity(entity_handle_accumilator)


def get_entity(entity_handle):
    for entity in entities:
        if entity.id == entity_handle:
            return entity
    
    return None


def create_texture(name, entity_handle, data, width, height, number_of_channels) -> Texture:
    global entity_handle_accumilator

    if number_of_channels == 1:
        format = GL_RED
    elif number_of_channels == 3:
        format = GL_RGB
    elif number_of_channels == 4:
        format = GL_RGBA
    else:
        # TODO(Miyuru): Handle error
        pass

    texture_id = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, texture_id)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
    glTexImage2D(GL_TEXTURE_2D, 0, format, width, height, 0, format, GL_UNSIGNED_BYTE, data)
    glGenerateMipmap(GL_TEXTURE_2D)

    return Texture(name, texture_id, entity_handle, data, 3)


def get_textures(entity_handle) -> list[Texture]:
    return [texture for texture in textures if texture.entity_handle == entity_handle]


def get_texture_width(texture_id):
    glBindTexture(GL_TEXTURE_2D, texture_id)
    width = glGetTexLevelParameteriv(GL_TEXTURE_2D, 0, GL_TEXTURE_WIDTH)
    glBindTexture(GL_TEXTURE_2D, 0)

    return width


def get_texture_height(texture_id):
    glBindTexture(GL_TEXTURE_2D, texture_id)
    height = glGetTexLevelParameteriv(GL_TEXTURE_2D, 0, GL_TEXTURE_HEIGHT)
    glBindTexture(GL_TEXTURE_2D, 0)

    return height


def load_image(file_path):
    image_surface = pygame.image.load(file_path)
    # image_surface = pygame.transform.flip(image_surface, False, True)
    image_data = pygame.image.tostring(image_surface, "RGB", True)
    width, height = image_surface.get_size()

    return image_data, width, height
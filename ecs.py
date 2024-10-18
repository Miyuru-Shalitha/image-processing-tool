import glm
import asset_manager
from OpenGL import GL


class Entity:
    def __init__(self, id: int) -> None:
        self.id: int = id


class TransformComponent:
    def __init__(self, entity_handle: int) -> None:
        self.entity_handle: int = entity_handle
        self.position: glm.vec2 = glm.vec2(0.0, 0.0)


class TextureComponent:
    def __init__(self, entity_handle: int) -> None:
        self.entity_handle: int = entity_handle
        self.textures: list[asset_manager.Texture] = []


class ColorManipulatorComponent:
    def __init__(self, entity_handle: int) -> None:
        self.entity_handle: int = entity_handle


class ImageTransformComponent:
    def __init__(self, entity_handle: int) -> None:
        self.entity_handle: int = entity_handle


entities: list[Entity] = []
transform_components: list[TransformComponent] = []
texture_components: list[TextureComponent] = []
color_manipulator_components: list[ColorManipulatorComponent] = []
image_transform_components: list[ImageTransformComponent] = []

entity_handle_count_accumilator: int = -1


def create_entity() -> Entity:
    global entity_handle_count_accumilator
    entity_handle_count_accumilator += 1
    entity = Entity(entity_handle_count_accumilator)
    entities.append(entity)

    return entity


def add_transform_component(entity_handle: int) -> TransformComponent:
    transform_component = TransformComponent(entity_handle)
    transform_components.append(transform_component)

    return transform_component


def add_texture_component(entity_handle: int) -> TextureComponent:
    texture = TextureComponent(entity_handle)
    texture_components.append(texture)

    return texture


def get_transform_component(entity_handle: int) -> TransformComponent | None:
    for transform_component in transform_components:
        if transform_component.entity_handle == entity_handle:
            return transform_component
        
    return None


def get_texture_component(entity_handle: int) -> TextureComponent | None:
    for texture_component in texture_components:
        if texture_component.entity_handle == entity_handle:
            return texture_component
    
    return None


def get_color_manipulator_component(entity_handle: int) -> ColorManipulatorComponent | None:
    for color_manipulator_component in color_manipulator_components:
        if color_manipulator_component.entity_handle == entity_handle:
            return color_manipulator_component
    
    return None


def get_image_transform_component(entity_handle: int) -> ImageTransformComponent | None:
    for image_transform_component in image_transform_components:
        if image_transform_component.entity_handle == entity_handle:
            return image_transform_component
    
    return None

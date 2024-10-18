import glm
import asset_manager
import image_processor


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
        self.texture_operations: list[image_processor.Operation] = []


class ColorManipulatorComponent:
    def __init__(self, entity_handle: int) -> None:
        self.entity_handle: int = entity_handle


class ImageTransformComponent:
    def __init__(self, entity_handle: int) -> None:
        self.entity_handle: int = entity_handle


class BoxFilterComponent:
    def __init__(self, entity_handle: int, kernel_size: tuple[int, int]) -> None:
        self.entity_handle: int = entity_handle
        self.kernel_size: tuple[int, int] = kernel_size
    

class GaussianFilterComponent:
    def __init__(self, entity_handle: int, kernel_size: int, sigma_x: float) -> None:
        self.entity_handle: int = entity_handle
        self.kernel_size: tuple[int, int] = kernel_size
        sigma_x: float = sigma_x


class EdgeDetectionComponent:
    def __init__(self, entity_handle: int, kernel_size: tuple[int, int]) -> None:
        self.entity_handle = entity_handle
        self.kernel_size: tuple[int, int] = kernel_size


class DenosingComponent:
    def __init__(self, entity_handle: int) -> None:
        self.entity_handle: int = entity_handle


entities: list[Entity] = []
transform_components: list[TransformComponent] = []
texture_components: list[TextureComponent] = []
color_manipulator_components: list[ColorManipulatorComponent] = []
image_transform_components: list[ImageTransformComponent] = []
box_filter_components: list[BoxFilterComponent] = []
gaussian_filter_components: list[GaussianFilterComponent] = []
edge_detection_components: list[EdgeDetectionComponent] = []
denoising_components: list[DenosingComponent] = []

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
    texture_component = TextureComponent(entity_handle)
    texture_components.append(texture_component)

    return texture_component


def add_image_transform_component(entity_handle: int) -> ImageTransformComponent:
    image_transform_component = ImageTransformComponent(entity_handle)
    image_transform_components.append(image_transform_component)

    return image_transform_component


def add_color_manipulator_component(entity_handle: int) -> ColorManipulatorComponent:
    color_manipulator_component = ColorManipulatorComponent(entity_handle)
    color_manipulator_components.append(color_manipulator_component)

    return color_manipulator_component


def add_box_filter_component(entity_handle: int) -> BoxFilterComponent:
    box_filter_component = BoxFilterComponent(entity_handle, (1, 1))
    box_filter_components.append(box_filter_component)

    return box_filter_component


def add_gaussian_filter_component(entity_handle: int) -> GaussianFilterComponent:
    gaussian_filter_component = GaussianFilterComponent(entity_handle, (1, 1), 1.0)
    gaussian_filter_components.append(gaussian_filter_component)

    return gaussian_filter_component


def add_edge_detection_component(entity_handle: int) -> EdgeDetectionComponent:
    edge_detection_component = EdgeDetectionComponent(entity_handle, (1, 1))
    edge_detection_components.append(edge_detection_component)

    return edge_detection_component


def add_denoising_component(entity_handle: int) -> DenosingComponent:
    denoising_component = DenosingComponent(entity_handle)
    denoising_components.append(denoising_component)

    return denoising_component


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


def get_box_filter_component(entity_handle: int) -> BoxFilterComponent | None:
    for box_filter_component in box_filter_components:
        if box_filter_component.entity_handle == entity_handle:
            return box_filter_component
    
    return None


def get_gaussian_filter_component(entity_handle: int) -> GaussianFilterComponent | None:
    for gaussian_filter_component in gaussian_filter_components:
        if gaussian_filter_component.entity_handle == entity_handle:
            return gaussian_filter_component
    
    return None


def get_edge_detection_component(entity_handle: int) -> EdgeDetectionComponent | None:
    for edge_detection_component in edge_detection_components:
        if edge_detection_component.entity_handle == entity_handle:
            return edge_detection_component
    
    return None


def get_denoising_component(entity_handle: int) -> DenosingComponent | None:
    for denoising_component in denoising_components:
        if denoising_component.entity_handle == entity_handle:
            return denoising_component
    
    return None

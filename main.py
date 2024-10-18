import pygame
import sys
import time
import imgui
import image_processor
import glm
import numpy as np
import ecs
import asset_manager
from imgui.integrations.pygame import PygameRenderer
from OpenGL import GL
from OpenGL.GL.shaders import compileProgram, compileShader 
from shaders import vertex_shader_source, fragment_shader_source
from tkinter import filedialog


vertices = np.array([
    # Positions       # UV coords
     0.5,  0.5, 0.0,  1.0, 1.0,  # Top right
     0.5, -0.5, 0.0,  1.0, 0.0,  # Bottom right
    -0.5, -0.5, 0.0,  0.0, 0.0,  # Bottom left
    -0.5,  0.5, 0.0,  0.0, 1.0   # Top left
], dtype='float32')

indices = np.array([
    0, 1, 2,  # First triangle
    0, 2, 3   # Second triangle
], dtype='uint32')


def main():
    pygame.init()
    pygame.display.set_mode((1280, 720), pygame.OPENGL | pygame.DOUBLEBUF | pygame.RESIZABLE)
    pygame.display.set_caption("Image Processing Tool")

    imgui.create_context()
    io = imgui.get_io()
    io.fonts.add_font_from_file_ttf('resources/fonts/Open_Sans/static/OpenSans-Regular.ttf', 18)
    renderer = PygameRenderer()

    vertex_array = GL.glGenVertexArrays(1)
    GL.glBindVertexArray(vertex_array)

    vertex_buffer = GL.glGenBuffers(1)
    GL.glBindBuffer(GL.GL_ARRAY_BUFFER, vertex_buffer)
    GL.glBufferData(GL.GL_ARRAY_BUFFER, vertices.nbytes, vertices, GL.GL_STATIC_DRAW)

    index_buffer = GL.glGenBuffers(1)
    GL.glBindBuffer(GL.GL_ELEMENT_ARRAY_BUFFER, index_buffer)
    GL.glBufferData(GL.GL_ELEMENT_ARRAY_BUFFER, indices.nbytes, indices, GL.GL_STATIC_DRAW)

    GL.glVertexAttribPointer(0, 3, GL.GL_FLOAT, GL.GL_FALSE, 5 * vertices.itemsize, None)
    GL.glEnableVertexAttribArray(0)

    GL.glVertexAttribPointer(1, 3, GL.GL_FLOAT, GL.GL_FALSE, 5 * vertices.itemsize, GL.ctypes.c_void_p(3 * vertices.itemsize))
    GL.glEnableVertexAttribArray(1)

    GL.glBindVertexArray(0)
    GL.glBindBuffer(GL.GL_ARRAY_BUFFER, 0)
    GL.glBindBuffer(GL.GL_ELEMENT_ARRAY_BUFFER, 0)
    GL.glDisableVertexAttribArray(0)
    GL.glDisableVertexAttribArray(1)

    vertex_shader = compileShader(vertex_shader_source, GL.GL_VERTEX_SHADER)
    fragment_shader = compileShader(fragment_shader_source, GL.GL_FRAGMENT_SHADER)
    shader_program = compileProgram(vertex_shader, fragment_shader)

    running = True

    selected_entity_handle = -1
    mouse_prev_position = glm.vec2(0.0, 0.0)
    mouse_flag = True
    mouse_sensitivity = 5.0
    mouse_scroll_sensitivity = 50.0
    
    camera_position = glm.vec3(0.0, 0.0, -3.0)

    prev_time = time.time()

    image_manipulator_color_mode_current_index = 0
    image_manipulator_color_modes = ["Original", "Gray scale"]

    image_transform_rotation = 0

    image_flip_vertically_checked = False
    image_flip_horizontally_checked = False

    box_filter_kernel_size = (1, 1)

    gaussian_filter_kernel_size = (1, 1)
    gaussian_filter_sigma_x = 1.0

    edge_detection_kernel_size = (1, 1)


    while running:
        current_time = time.time()
        dt = current_time - prev_time
        prev_time = current_time

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            renderer.process_event(event)

        if io.mouse_down[1]:
            for texture in asset_manager.textures:
                mouse_current_position = glm.vec2(io.mouse_pos.x, io.mouse_pos.y)
                mouse_position_delta = mouse_current_position - mouse_prev_position
                mouse_prev_position = mouse_current_position

                if not mouse_flag:
                    mouse_flag = True
                    camera_position += glm.vec3(mouse_position_delta.x, -mouse_position_delta.y, 0.0) * dt * mouse_sensitivity

                mouse_flag = False
        else:
            mouse_flag = True
            mouse_current_position = glm.vec2(0.0, 0.0)
        
        if io.mouse_wheel != 0:
            camera_position.z += io.mouse_wheel * dt * mouse_scroll_sensitivity

        window_size = pygame.display.get_window_size()
        GL.glViewport(0, 0, window_size[0], window_size[1])
        GL.glClearColor(0.3, 0.3, 0.3, 1.0)
        GL.glClear(GL.GL_COLOR_BUFFER_BIT)

        view = glm.mat4(1.0)
        view = glm.translate(view, camera_position)
        projection = glm.perspective(45.0, window_size[0] / window_size[1], 0.1, 100.0)

        for entity in ecs.entities:
            transform_component: ecs.TransformComponent = ecs.get_transform_component(entity.id)
            texture_component: ecs.TextureComponent = ecs.get_texture_component(entity.id)
            texture: asset_manager.Texture = texture_component.textures[-1]
            GL.glUseProgram(shader_program)
            
            model = glm.mat4(1.0)
            model = glm.translate(model, glm.vec3(transform_component.position, 0.0))
            model = glm.scale(
                model, 
                glm.vec3(
                    asset_manager.get_texture_width(texture.id) / 1000.0, 
                    asset_manager.get_texture_height(texture.id) / 1000.0, 
                    0.0
                )
            )
            
            model_location = GL.glGetUniformLocation(shader_program, "model")
            view_location = GL.glGetUniformLocation(shader_program, "view")
            projection_location = GL.glGetUniformLocation(shader_program, "projection")
            texture_location = GL.glGetUniformLocation(shader_program, "diffuse")
            number_of_channel_location = GL.glGetUniformLocation(shader_program, "number_of_channels")
            
            GL.glUniformMatrix4fv(model_location, 1, GL.GL_FALSE, glm.value_ptr(model))
            GL.glUniformMatrix4fv(view_location, 1, GL.GL_FALSE, glm.value_ptr(view))
            GL.glUniformMatrix4fv(projection_location, 1, GL.GL_FALSE, glm.value_ptr(projection))
            GL.glUniform1i(number_of_channel_location, texture.number_of_channels)
            GL.glActiveTexture(GL.GL_TEXTURE0)
            GL.glBindTexture(GL.GL_TEXTURE_2D, texture.id)
            GL.glUniform1i(texture_location, 0)

            GL.glBindVertexArray(vertex_array)
            GL.glDrawElements(GL.GL_TRIANGLES, 6, GL.GL_UNSIGNED_INT, None)
            GL.glBindVertexArray(0)
            GL.glUseProgram(0)

        io.display_size = pygame.display.get_window_size()
        renderer.process_inputs()
        imgui.new_frame()

        ########## Item list window begin ##########
        imgui.begin("Item List Window")

        for entity in ecs.entities:
            texture: ecs.TextureComponent = ecs.get_texture_component(entity.id)
            first_texture_name: str = ecs.get_texture_component(entity.id).textures[0].name
            _, is_selected = imgui.selectable(first_texture_name, entity.id == selected_entity_handle)

            if is_selected:
                selected_entity_handle = entity.id


        if imgui.button("Add Image"):
            file_path = filedialog.askopenfilename()

            if file_path:
                image: asset_manager.Image = asset_manager.load_image(file_path)
                texture: asset_manager.Texture = asset_manager.create_texture(
                    image.name,
                    image.data,
                    image.width, 
                    image.height,
                    image.number_of_channels
                )
                entity: ecs.Entity = ecs.create_entity()
                ecs.add_transform_component(entity.id)
                texture_component: ecs.TextureComponent = ecs.add_texture_component(entity.id)
                texture_component.textures.append(texture)

        imgui.end()
        ########### Item list window end ###########

        ########## Inspector window begin ##########
        imgui.begin("Inspector Window")
        for entity in ecs.entities:
            if entity.id == selected_entity_handle:
                transform_component: ecs.TransformComponent = ecs.get_transform_component(entity.id)
                texture_component: ecs.TextureComponent = ecs.get_texture_component(entity.id)
                last_texture: asset_manager.Texture = texture_component.textures[-1]

                if imgui.tree_node("Image", imgui.TREE_NODE_DEFAULT_OPEN | imgui.TREE_NODE_SPAN_AVAILABLE_WIDTH):
                    if imgui.begin_table("Image", 2):
                        # Row - 1
                        imgui.table_next_row()

                        imgui.table_next_column()
                        imgui.text("Header 0")
                        
                        imgui.table_next_column()
                        imgui.text("Header 1")

                        # Row - 2
                        imgui.table_next_row()

                        imgui.table_next_column()
                        imgui.text("Position")
                        
                        imgui.table_next_column()
                        _, (transform_component.position.x, transform_component.position.y) = imgui.drag_float2(
                            "##Position", 
                            transform_component.position.x, 
                            transform_component.position.y
                        )
                        
                        imgui.end_table()

                    imgui.tree_pop()
            
                if  ecs.get_color_manipulator_component(entity.id) is not None and \
                    imgui.tree_node("Color Manipulator", imgui.TREE_NODE_DEFAULT_OPEN | imgui.TREE_NODE_SPAN_AVAILABLE_WIDTH):
                    if imgui.begin_table("Color Manipulator", 2):
                        # Row - 1
                        imgui.table_next_row()

                        imgui.table_next_column()
                        imgui.text("Color mode")

                        imgui.table_next_column()
                        is_clicked, image_manipulator_color_mode_current_index = imgui.combo("##Color mode", image_manipulator_color_mode_current_index, image_manipulator_color_modes)

                        if is_clicked:
                            if image_manipulator_color_modes[image_manipulator_color_mode_current_index] == "Original":
                                found_operation = None

                                for texture_opration in texture_component.texture_operations:
                                    if texture_opration.operation_type == image_processor.OperationType.CONVERT_TO_GRAY_SCALE:
                                        found_operation = texture_opration
                                        break
                                
                                if found_operation is not None:
                                    for texture in texture_component.textures:
                                        if texture.id == found_operation.texture_id:
                                            texture_component.textures.remove(texture)
                                            texture_component.texture_operations.remove(found_operation)

                            elif image_manipulator_color_modes[image_manipulator_color_mode_current_index] == "Gray scale":
                                texture_component: ecs.TextureComponent = ecs.get_texture_component(selected_entity_handle)
                                last_texture: asset_manager.Texture = texture_component.textures[-1]
                                gray_image_data = image_processor.change_color_mode(
                                    last_texture.data, 
                                    asset_manager.get_texture_width(last_texture.id),
                                    asset_manager.get_texture_height(last_texture.id),
                                    3
                                )
                                gray_texture = asset_manager.create_texture(
                                    f"{last_texture.name} (BW)", 
                                    gray_image_data, 
                                    asset_manager.get_texture_width(last_texture.id), # Same width as the original texture
                                    asset_manager.get_texture_height(last_texture.id), # Same height as the original texture
                                    1
                                )
                                texture_component.textures.append(gray_texture)
                                gray_scale_opration = image_processor.Operation(texture_component.entity_handle, gray_texture.id, image_processor.OperationType.CONVERT_TO_GRAY_SCALE)
                                texture_component.texture_operations.append(gray_scale_opration)                                

                        imgui.end_table()

                    imgui.tree_pop()
                
                if ecs.get_image_transform_component(selected_entity_handle) and \
                    imgui.tree_node("Image Transform", imgui.TREE_NODE_DEFAULT_OPEN | imgui.TREE_NODE_SPAN_AVAILABLE_WIDTH):
                    if imgui.begin_table("Image Transform", 2):
                        # Row - 1
                        imgui.table_next_row()

                        imgui.table_next_column()
                        imgui.text("Rotation")

                        imgui.table_next_column()
                        is_changed, image_transform_rotation = imgui.slider_angle("##Rotation", image_transform_rotation, value_degrees_min=0.0, value_degrees_max=360.0)

                        if is_changed:
                            rotated_image_data = image_processor.rotate_image(
                                last_texture.data,
                                asset_manager.get_texture_width(last_texture.id),
                                asset_manager.get_texture_height(last_texture.id),
                                image_transform_rotation,
                                last_texture.number_of_channels
                            )

                            found_operation = None

                            for operation in texture_component.texture_operations:
                                if operation.operation_type == image_processor.OperationType.ROTATE:
                                    found_operation = operation
                                    break

                            if found_operation is not None:
                                last_texture.data = rotated_image_data
                            else:
                                rotated_texture = asset_manager.create_texture(
                                    f"{last_texture.name} (Rotated - {image_transform_rotation})",
                                    rotated_image_data,
                                    asset_manager.get_texture_width(last_texture.id),
                                    asset_manager.get_texture_height(last_texture.id),
                                    last_texture.number_of_channels
                                ) 
                                texture_component.textures.append(rotated_texture)
                                rotated_operation = image_processor.Operation(selected_entity_handle, rotated_texture.id, image_processor.OperationType.ROTATE)
                                texture_component.texture_operations.append(rotated_operation)

                        imgui.table_next_row()

                        imgui.table_next_column()
                        imgui.text("Flip vertically")
                        
                        imgui.table_next_column()
                        changed, image_flip_vertically_checked = imgui.checkbox("##flip vertically", image_flip_vertically_checked)
                        
                        if changed:
                            flipped_image_data = image_processor.flip_image_vertically(
                                last_texture.data,
                                asset_manager.get_texture_width(last_texture.id),
                                asset_manager.get_texture_height(last_texture.id),
                                last_texture.number_of_channels
                            )
                            flipped_texture = asset_manager.create_texture(
                                f"{last_texture.name} - Flipped vertically",
                                flipped_image_data,
                                asset_manager.get_texture_width(last_texture.id),
                                asset_manager.get_texture_height(last_texture.id),
                                last_texture.number_of_channels
                            )
                            texture_component.textures.append(flipped_texture)
                            flipped_vertically_operation = image_processor.Operation(selected_entity_handle, flipped_texture.id, image_processor.OperationType.FLIP_VERTICALLY)
                            texture_component.texture_operations.append(flipped_vertically_operation)

                        imgui.table_next_row()

                        imgui.table_next_column()
                        imgui.text("Flip horizontally")

                        imgui.table_next_column()
                        changed, image_flip_horizontally_checked = imgui.checkbox("##flip horizontally", image_flip_horizontally_checked)

                        if changed:
                            flipped_image_data = image_processor.flip_image_horizontally(
                                last_texture.data,
                                asset_manager.get_texture_width(last_texture.id),
                                asset_manager.get_texture_height(last_texture.id),
                                last_texture.number_of_channels
                            )
                            flipped_texture = asset_manager.create_texture(
                                f"{last_texture.name} - Flipped horizontally",
                                flipped_image_data,
                                asset_manager.get_texture_width(last_texture.id),
                                asset_manager.get_texture_height(last_texture.id),
                                last_texture.number_of_channels
                            )
                            texture_component.textures.append(flipped_texture)
                            flipped_vertically_operation = image_processor.Operation(selected_entity_handle, flipped_texture.id, image_processor.OperationType.FLIP_HORIZONTALLY)
                            texture_component.texture_operations.append(flipped_vertically_operation)

                        imgui.end_table()

                    imgui.tree_pop()

                if ecs.get_box_filter_component(selected_entity_handle) and \
                    imgui.tree_node("Box Filter", imgui.TREE_NODE_DEFAULT_OPEN | imgui.TREE_NODE_SPAN_AVAILABLE_WIDTH):
                    if imgui.begin_table("Box Filter", 2):
                        imgui.table_next_row()

                        imgui.table_next_column()
                        imgui.text("Kernel")

                        imgui.table_next_column()
                        kernel_size_changed, box_filter_kernel_size = imgui.input_int2("##Kernel", box_filter_kernel_size[0], box_filter_kernel_size[1])

                        if kernel_size_changed:
                            box_filtered_image_data = image_processor.box_filter(
                                last_texture.data, 
                                asset_manager.get_texture_width(last_texture.id),
                                asset_manager.get_texture_height(last_texture.id),
                                last_texture.number_of_channels,
                                box_filter_kernel_size
                            )
                            box_filtered_texture = asset_manager.create_texture(
                                f"{last_texture.name} - Box filtered ({box_filter_kernel_size[0], box_filter_kernel_size[1]})",
                                box_filtered_image_data,
                                asset_manager.get_texture_width(last_texture.id),
                                asset_manager.get_texture_height(last_texture.id),
                                last_texture.number_of_channels
                            )
                            texture_component.textures.append(box_filtered_texture)
                            box_filter_operation = image_processor.Operation(selected_entity_handle, box_filtered_texture.id, image_processor.OperationType.BOX_FILTER)
                            texture_component.texture_operations.append(box_filter_operation)

                        imgui.end_table()

                    imgui.tree_pop()
                    
                if ecs.get_gaussian_filter_component(selected_entity_handle) and \
                    imgui.tree_node("Gaussian Filter", imgui.TREE_NODE_DEFAULT_OPEN | imgui.TREE_NODE_SPAN_AVAILABLE_WIDTH):
                    if imgui.begin_table("Gaussian Filter", 2):
                        imgui.table_next_row()

                        imgui.table_next_column()
                        imgui.text("Kernel")

                        imgui.table_next_column()
                        kernel_size_changed, gaussian_filter_kernel_size = imgui.input_int2("##Kernel", gaussian_filter_kernel_size[0], gaussian_filter_kernel_size[1])

                        if kernel_size_changed:
                            gaussian_filtered_image_data = image_processor.gaussian_filter(
                                last_texture.data, 
                                asset_manager.get_texture_width(last_texture.id),
                                asset_manager.get_texture_height(last_texture.id),
                                last_texture.number_of_channels,
                                gaussian_filter_kernel_size,
                                gaussian_filter_sigma_x
                            )
                            gaussian_filtered_texture = asset_manager.create_texture(
                                f"{last_texture.name} - Gaussian filtered ({gaussian_filter_kernel_size[0]}, {gaussian_filter_kernel_size[1]}, {gaussian_filter_sigma_x})",
                                gaussian_filtered_image_data,
                                asset_manager.get_texture_width(last_texture.id),
                                asset_manager.get_texture_height(last_texture.id),
                                last_texture.number_of_channels
                            )
                            texture_component.textures.append(gaussian_filtered_texture)
                            gaussian_filter_operation = image_processor.Operation(selected_entity_handle, gaussian_filtered_texture.id, image_processor.OperationType.GAUSSIAN_FILTER)
                            texture_component.texture_operations.append(gaussian_filter_operation)
                        
                        imgui.table_next_row()

                        imgui.table_next_column()
                        imgui.text("Sigma X")

                        imgui.table_next_column()
                        sigma_x_changed, gaussian_filter_sigma_x = imgui.input_int("##Sigma X", gaussian_filter_sigma_x)

                        if sigma_x_changed:
                            gaussian_filtered_image_data = image_processor.gaussian_filter(
                                last_texture.data, 
                                asset_manager.get_texture_width(last_texture.id),
                                asset_manager.get_texture_height(last_texture.id),
                                last_texture.number_of_channels,
                                gaussian_filter_kernel_size,
                                gaussian_filter_sigma_x
                            )
                            gaussian_filtered_texture = asset_manager.create_texture(
                                f"{last_texture.name} - Gaussian filtered ({gaussian_filter_kernel_size[0]}, {gaussian_filter_kernel_size[1]}, {gaussian_filter_sigma_x})",
                                gaussian_filtered_image_data,
                                asset_manager.get_texture_width(last_texture.id),
                                asset_manager.get_texture_height(last_texture.id),
                                last_texture.number_of_channels
                            )
                            texture_component.textures.append(gaussian_filtered_texture)
                            gaussian_filter_operation = image_processor.Operation(selected_entity_handle, gaussian_filtered_texture.id, image_processor.OperationType.GAUSSIAN_FILTER)
                            texture_component.texture_operations.append(gaussian_filter_operation)

                        imgui.end_table()
                    
                    imgui.tree_pop()

                if ecs.get_edge_detection_component(selected_entity_handle) and \
                    imgui.tree_node("Edge Detection", imgui.TREE_NODE_DEFAULT_OPEN | imgui.TREE_NODE_SPAN_AVAILABLE_WIDTH):
                    if imgui.begin_table("Edge Detection", 2):
                        imgui.table_next_row()

                        imgui.table_next_column()
                        imgui.text("Kernel")

                        imgui.table_next_column()
                        kernel_size_changed, edge_detection_kernel_size = imgui.input_int2("##Kernel", edge_detection_kernel_size[0], edge_detection_kernel_size[1])

                        if kernel_size_changed:
                            edge_detected_image_data = image_processor.sobel_edge_ditection(
                                last_texture.data, 
                                asset_manager.get_texture_width(last_texture.id),
                                asset_manager.get_texture_height(last_texture.id),
                                last_texture.number_of_channels
                            )
                            edge_detected_texture = asset_manager.create_texture(
                                f"{last_texture.name} - Edget detection ({edge_detection_kernel_size[0]}, {edge_detection_kernel_size[1]})",
                                edge_detected_image_data,
                                asset_manager.get_texture_width(last_texture.id),
                                asset_manager.get_texture_height(last_texture.id),
                                1 # Image is in gray scale
                            )
                            texture_component.textures.append(edge_detected_texture)
                            edge_detection_operation = image_processor.Operation(selected_entity_handle, edge_detected_texture.id, image_processor.OperationType.EDGE_DETECTION)
                            texture_component.texture_operations.append(edge_detection_operation)

                        imgui.end_table()

                    imgui.tree_pop()

                if ecs.get_denoising_component(selected_entity_handle) and \
                    imgui.tree_node("Denoising", imgui.TREE_NODE_DEFAULT_OPEN | imgui.TREE_NODE_SPAN_AVAILABLE_WIDTH):
                    if imgui.begin_table("Denoising", 2):
                        imgui.table_next_row()

                        imgui.table_next_column()
                        imgui.text("Denoise")

                        imgui.table_next_column()
                        if imgui.button("Denoise"):

                            denoised_image_data = image_processor.denoise_image(
                                last_texture.data,
                                asset_manager.get_texture_width(last_texture.id),
                                asset_manager.get_texture_height(last_texture.id),
                                last_texture.number_of_channels
                            )
                            denoised_texture = asset_manager.create_texture(
                                f"{last_texture.name} - (Denoise)",
                                denoised_image_data,
                                asset_manager.get_texture_width(last_texture.id),
                                asset_manager.get_texture_height(last_texture.id),
                                last_texture.number_of_channels 
                            )
                            texture_component.textures.append(denoised_texture)
                            denoised_operation = image_processor.Operation(selected_entity_handle, denoised_texture.id, image_processor.OperationType.DENOISING)
                            texture_component.texture_operations.append(denoised_operation)

                        imgui.end_table()

                    imgui.tree_pop()

        if imgui.button("Add Component"):
            imgui.open_popup("Components Menu")
        
        if imgui.begin_popup("Components Menu"):
            color_manipulator_menu_item = imgui.menu_item("Color Manipulator")
            if color_manipulator_menu_item[0]:
                ecs.add_color_manipulator_component(selected_entity_handle)
            
            image_transform_menu_item = imgui.menu_item("Image Transform")
            if image_transform_menu_item[0]:
                ecs.add_image_transform_component(selected_entity_handle)

            box_filter_menu_item = imgui.menu_item("Box Filter")
            if box_filter_menu_item[0]:
                ecs.add_box_filter_component(selected_entity_handle)
            
            gaussian_filter_menu_item = imgui.menu_item("Gaussian Filter")
            if gaussian_filter_menu_item[0]:
                ecs.add_gaussian_filter_component(selected_entity_handle)
            
            edge_detection_menu_item = imgui.menu_item("Edge Detection")
            if edge_detection_menu_item[0]:
                ecs.add_edge_detection_component(selected_entity_handle)            

            denoising_menu_item = imgui.menu_item("Denoising")
            if denoising_menu_item[0]:
                ecs.add_denoising_component(selected_entity_handle)
            
            imgui.end_popup()

        imgui.end()
        ########### Inspector window end ###########

        imgui.render()
        renderer.render(imgui.get_draw_data())
        # imgui.end_frame()

        pygame.display.flip()


    renderer.shutdown()
    pygame.quit()
    sys.exit(0)


if __name__ == '__main__':
    main()

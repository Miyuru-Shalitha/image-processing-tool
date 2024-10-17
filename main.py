import pygame
import sys
import time
import imgui
import image_processor
import glm
import numpy as np
import asset_manager
from imgui.integrations.pygame import PygameRenderer
from OpenGL.GL import *
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

    vertex_array = glGenVertexArrays(1)
    glBindVertexArray(vertex_array)

    vertex_buffer = glGenBuffers(1)
    glBindBuffer(GL_ARRAY_BUFFER, vertex_buffer)
    glBufferData(GL_ARRAY_BUFFER, vertices.nbytes, vertices, GL_STATIC_DRAW)

    index_buffer = glGenBuffers(1)
    glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, index_buffer)
    glBufferData(GL_ELEMENT_ARRAY_BUFFER, indices.nbytes, indices, GL_STATIC_DRAW)

    glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 5 * vertices.itemsize, None)
    glEnableVertexAttribArray(0)

    glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, 5 * vertices.itemsize, ctypes.c_void_p(3 * vertices.itemsize))
    glEnableVertexAttribArray(1)

    glBindVertexArray(0)
    glBindBuffer(GL_ARRAY_BUFFER, 0)
    glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, 0)
    glDisableVertexAttribArray(0)
    glDisableVertexAttribArray(1)

    vertex_shader = compileShader(vertex_shader_source, GL_VERTEX_SHADER)
    fragment_shader = compileShader(fragment_shader_source, GL_FRAGMENT_SHADER)
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
    image_manipulator_color_modes = ["Original", "Black and white"]


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
        glViewport(0, 0, window_size[0], window_size[1])
        glClearColor(0.3, 0.3, 0.3, 1.0)
        glClear(GL_COLOR_BUFFER_BIT)

        view = glm.mat4(1.0)
        view = glm.translate(view, camera_position)
        projection = glm.perspective(45.0, window_size[0] / window_size[1], 0.1, 100.0)

        for entity in asset_manager.entities:
            texture = asset_manager.get_textures(entity.id)[-1]
            glUseProgram(shader_program)
            
            model = glm.mat4(1.0)
            model = glm.translate(model, glm.vec3(texture.position, 0.0))
            model = glm.scale(
                model, 
                glm.vec3(
                    asset_manager.get_texture_width(texture.id) / 1000.0, 
                    asset_manager.get_texture_height(texture.id) / 1000.0, 
                    0.0
                )
            )
            
            model_location = glGetUniformLocation(shader_program, "model")
            view_location = glGetUniformLocation(shader_program, "view")
            projection_location = glGetUniformLocation(shader_program, "projection")
            texture_location = glGetUniformLocation(shader_program, "diffuse")
            
            glUniformMatrix4fv(model_location, 1, GL_FALSE, glm.value_ptr(model))
            glUniformMatrix4fv(view_location, 1, GL_FALSE, glm.value_ptr(view))
            glUniformMatrix4fv(projection_location, 1, GL_FALSE, glm.value_ptr(projection))
            glActiveTexture(GL_TEXTURE0)
            glBindTexture(GL_TEXTURE_2D, texture.id)
            glUniform1i(texture_location, 0)

            glBindVertexArray(vertex_array)
            glDrawElements(GL_TRIANGLES, 6, GL_UNSIGNED_INT, None)
            glBindVertexArray(0)
            glUseProgram(0)

        io.display_size = pygame.display.get_window_size()
        renderer.process_inputs()
        imgui.new_frame()

        ########## Item list window begin ##########
        imgui.begin("Item List Window")

        for entity in asset_manager.entities:
            texture = asset_manager.get_textures(entity.id)[0]
            _, is_selected = imgui.selectable(texture.name, texture.id == selected_entity_handle)

            if is_selected:
                selected_entity_handle = entity.id


        if imgui.button("Add Image"):
            file_path = filedialog.askopenfilename()

            if file_path:
                texture_data, width, height = asset_manager.load_image(file_path)
                entity = asset_manager.create_entity()
                texture = asset_manager.create_texture(file_path.split('/')[-1], entity.id, texture_data, width, height, 3)
                texture.entity_handle = entity.id
                asset_manager.entities.append(entity)
                asset_manager.textures.append(texture)

        imgui.end()
        ########### Item list window end ###########

        ########## Inspector window begin ##########
        imgui.begin("Inspector Window")
        for entity in asset_manager.entities:
            if entity.id == selected_entity_handle:
                texture = asset_manager.get_textures(entity.id)[-1]

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
                        _, (texture.position.x, texture.position.y) = imgui.drag_float2("##Position", texture.position.x, texture.position.y)
                        
                        imgui.end_table()

                    imgui.tree_pop()
            
                if (asset_manager.ComponentType.COLOR_MANIPULATOR_COMPONENT in entity.components) and \
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
                                asset_manager.textures.pop() # Add an id for each operation(texture) and check the item and remove it from textures :)
                            elif image_manipulator_color_modes[image_manipulator_color_mode_current_index] == "Black and white":
                                gray_image_data = image_processor.change_color_mode(
                                    texture.data, 
                                    asset_manager.get_texture_width(texture.id),
                                    asset_manager.get_texture_height(texture.id),
                                    image_processor.ColorMode.BW
                                )
                                gray_texture = asset_manager.create_texture(
                                    f"{texture.name} (BW)", 
                                    entity.id,
                                    gray_image_data, 
                                    asset_manager.get_texture_width(texture.id), # Same width as the original texture
                                    asset_manager.get_texture_height(texture.id), # Same height as the original texture
                                    1
                                )
                                asset_manager.textures.append(gray_texture)

                        imgui.end_table()

                    imgui.tree_pop()
                
                if (asset_manager.ComponentType.IMAGE_TRANSFORM_COMPONENT in entity.components) and \
                    imgui.tree_node("Image Transform", imgui.TREE_NODE_DEFAULT_OPEN | imgui.TREE_NODE_SPAN_AVAILABLE_WIDTH):
                    if imgui.begin_table("Image Transform", 2):
                        # Row - 1
                        imgui.table_next_row()

                        imgui.table_next_column()
                        imgui.text("Rotation")

                        imgui.table_next_column()
                        imgui.text("0")

                        imgui.end_table()

                    imgui.tree_pop()

            if imgui.button("Add Component"):
                imgui.open_popup("Components Menu")
            
            if imgui.begin_popup("Components Menu"):
                imgui.text("Basics")

                color_manipulator_menu_item = imgui.menu_item("Color Manipulator")

                if color_manipulator_menu_item[0]:
                    entity.components.append(asset_manager.ComponentType.COLOR_MANIPULATOR_COMPONENT)
                
                image_transform_menu_item = imgui.menu_item("Image Transform")

                if image_transform_menu_item[0]:
                    entity.components.append(asset_manager.ComponentType.IMAGE_TRANSFORM_COMPONENT)
                
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

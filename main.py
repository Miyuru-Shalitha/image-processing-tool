import pygame
import sys
import imgui
import numpy as np
from imgui.integrations.pygame import PygameRenderer
from OpenGL.GL import *
from OpenGL.GL.shaders import compileProgram, compileShader 
from shaders import vertex_shader_source, fragment_shader_source


vertices = np.array([
    # Positions       # Texture coords
    0.5, 0.5, 0.0,     1.0,  1.0,  # Top right
    0.5, -0.5, 0.0,    1.0,  0.0,  # Bottom right
    -0.5, -0.5, 0.0,   0.0, -1.0,  # Bottom left
    -0.5, 0.5, 0.0,   -1.0, -1.0   # Top left
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

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            renderer.process_event(event)

        glClearColor(0.3, 0.3, 0.3, 1.0)
        glClear(GL_COLOR_BUFFER_BIT)

        glUseProgram(shader_program)
        glBindVertexArray(vertex_array)
        glDrawElements(GL_TRIANGLES, 6, GL_UNSIGNED_INT, None)
        glBindVertexArray(0)
        glUseProgram(0)

        io.display_size = pygame.display.get_window_size()
        renderer.process_inputs()
        imgui.new_frame()

        imgui.begin("Inspector")
        imgui.button("Click")
        imgui.end()

        imgui.render()
        renderer.render(imgui.get_draw_data())
        # imgui.end_frame()

        pygame.display.flip()


    renderer.shutdown()
    pygame.quit()
    sys.exit(0)


if __name__ == '__main__':
    main()

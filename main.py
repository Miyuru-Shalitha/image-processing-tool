import pygame
import sys
import imgui
from imgui.integrations.pygame import PygameRenderer
from OpenGL.GL import *


def main():
    pygame.init()
    screen = pygame.display.set_mode((1280, 720), pygame.OPENGL | pygame.DOUBLEBUF)
    pygame.display.set_caption("Image Processing Tool")

    imgui.create_context()
    io = imgui.get_io()
    io.fonts.add_font_from_file_ttf('resources/fonts/Open_Sans/static/OpenSans-Regular.ttf', 18)
    renderer = PygameRenderer()

    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            renderer.process_event(event)

        glClearColor(0.3, 0.3, 0.3, 1.0)
        glClear(GL_COLOR_BUFFER_BIT)

        io.display_size = pygame.display.get_window_size()
        
        renderer.process_inputs()
        imgui.new_frame()

        imgui.begin("Inspector")
        imgui.button("Click")
        imgui.end()

        imgui.render()
        renderer.render(imgui.get_draw_data())
        imgui.end_frame()

        pygame.display.flip()


    renderer.shutdown()
    pygame.quit()
    sys.exit(0)


if __name__ == '__main__':
    main()

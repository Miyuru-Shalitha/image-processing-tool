vertex_shader_source = """
#version 460

layout (location=0) in vec3 position;
layout (location=1) in vec2 tex_coords;

out vec2 v_tex_coords;

void main() {
    gl_Position = vec4(position, 1.0);
    v_tex_coords = tex_coords;
}
"""

fragment_shader_source = """
#version 460

in vec2 v_tex_coords;

out vec4 frag_color;

void main() {
    frag_color = vec4(1.0, 1.0, 0.0, 1.0);
}
"""
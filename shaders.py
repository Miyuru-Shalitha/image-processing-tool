vertex_shader_source = """
#version 460

layout (location=0) in vec3 position;
layout (location=1) in vec2 tex_coords;

out vec2 v_tex_coords;

uniform mat4 model;
uniform mat4 view;
uniform mat4 projection;

void main() {
    gl_Position = projection * view * model * vec4(position, 1.0);
    v_tex_coords = tex_coords;
}
"""

fragment_shader_source = """
#version 460

in vec2 v_tex_coords;

out vec4 frag_color;

uniform sampler2D diffuse;

void main() {
    frag_color = texture(diffuse, v_tex_coords);
}
"""
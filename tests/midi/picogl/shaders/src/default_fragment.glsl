#version 330 core

in vec3 fragmentColor;
out vec4 color;

void main() {
    float dist = length(gl_PointCoord - vec2(0.5));
    if (dist > 0.5)
        discard;
    color = vec4(fragmentColor, 1.0);
}
/*
 * Script to draw two color triangles using WebGL 2 and TWGL
 * Gilberto Echeverria (modificado)
 * 2025-11-05
 */

'use strict';

import * as twgl from 'twgl-base.js';

// Vertex Shader
const vsGLSL = `#version 300 es
in vec4 a_position;
in vec4 a_color;

out vec4 v_color;

void main() {
    gl_Position = a_position;
    v_color = a_color;
}
`;

// Fragment Shader
const fsGLSL = `#version 300 es
precision highp float;

in vec4 v_color;
out vec4 outColor;

void main() {
    outColor = v_color;
}
`;

function main_twgl() {
    const canvas = document.querySelector('canvas');
    const gl = canvas.getContext('webgl2');

    const programInfo = twgl.createProgramInfo(gl, [vsGLSL, fsGLSL]);

    const arrays = generateData();
    const bufferInfo = twgl.createBufferInfoFromArrays(gl, arrays);
    const vao = twgl.createVAOFromBufferInfo(gl, programInfo, bufferInfo);

    gl.bindVertexArray(vao);
    gl.useProgram(programInfo.program);

    // Configurar el viewport y limpiar la pantalla
    gl.viewport(0, 0, canvas.width, canvas.height);
    gl.clearColor(0.1, 0.1, 0.1, 1);
    gl.clear(gl.COLOR_BUFFER_BIT);

    // Dibujar los dos triángulos (6 vértices)
    twgl.drawBufferInfo(gl, bufferInfo);
}

// Datos para dos triángulos de colores
function generateData() {
    return {
        a_position: {
            numComponents: 2,
            data: new Float32Array([
                // Primer triángulo
                0,    0.7,
                0.5, -0.7,
                -0.5, -0.7,
                // Segundo triángulo
                0,    0.2,
                0.8, -0.5,
                -0.3, -0.8,
            ]),
        },
        a_color: {
            numComponents: 4,
            type: Uint8Array,          // importante
            normalized: true,          // convierte [0,255] → [0,1]
            data: new Uint8Array([
                // Colores del primer triángulo
                255, 0, 0, 255,      // Rojo
                0, 255, 0, 255,      // Verde
                0, 0, 255, 255,      // Azul
                // Colores del segundo triángulo
                255, 255, 0, 255,    // Amarillo
                255, 0, 255, 255,    // Magenta
                0, 255, 255, 255,    // Cian
            ]),
        },
    };
}

main_twgl();

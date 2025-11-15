// Amilka Daniela Lopez Aguilar A01029277 Intentando crear el monstruo come galletas 
// y que la galleta sea un pivote. 
'use strict';

import * as twgl from 'twgl-base.js';
import GUI from 'lil-gui';
import { M3 } from './2d-lib.js';

// Vertex Shader as a string
const vsGLSL = `#version 300 es
in vec2 a_position;
in vec4 a_color;

uniform vec2 u_resolution;
uniform mat3 u_transforms;

out vec4 v_color;

void main() {

    vec2 pos = (u_transforms * vec3(a_position, 1)).xy;

    vec2 zeroToOne = pos / u_resolution;
    vec2 zeroToTwo = zeroToOne * 2.0;
    vec2 clipSpace = zeroToTwo - 1.0;

    gl_Position = vec4(clipSpace * vec2(1, -1), 0, 1);
    v_color = a_color;
}
`;

const fsGLSL = `#version 300 es
precision highp float;

in vec4 v_color;
out vec4 outColor;

void main() {
  outColor = v_color;
}
`;
// Declarar cada objeto como un array con el contenido que necesita

function makeCircle(cx, cy, r, sides, color) {
    const arr = {
        a_position: { numComponents: 2, data: [] },
        a_color:    { numComponents: 4, data: [] },
        indices:    { numComponents: 3, data: [] },
    };

// Inicializamos
    arr.a_position.data.push(cx, cy);
    // operador ... javascript para pasar todos los elementos dentro del array https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Operators/Spread_syntax
    arr.a_color.data.push(...color); 

    const angleStep = Math.PI * 2 / sides;

// loop over the sides to create the rest of the vertices, codigo adaptado de viewport-twgl que tenia el poligono
    for (let i = 0; i < sides; i++) {
        const a = i * angleStep;
        arr.a_position.data.push(cx + Math.cos(a) * r);
        arr.a_position.data.push(cy + Math.sin(a) * r);
        arr.a_color.data.push(...color);
        arr.indices.data.push(0, i + 1, (i + 2 <= sides ? i + 2 : 1));
    }

    return arr;
}

// Monstruo come galletas que usa makecirle
function makeCookieMonster() {

    const parts = [];

    // cuerpo (o cabeza?) azul con make circle, que recibe cx, cy, radio, sides y un color (azul en RGBA)
    parts.push(makeCircle(250, 250, 120, 40, [0, 0.3, 1, 1]));

    //lo mismo para generar las circunferencias de los ojos, posicionadas de tal forma que se vean como ojos
    parts.push(makeCircle(220, 300, 25, 20, [1, 1, 1, 1]));
    parts.push(makeCircle(280, 300, 25, 20, [1, 1, 1, 1]));

    // y pupilas
    parts.push(makeCircle(220, 300, 10, 20, [0, 0, 0, 1]));
    parts.push(makeCircle(280, 300, 10, 20, [0, 0, 0, 1]));

    // La boca. Hubiera estado cool hacerla un semicirculo 
    const mouth = makeCircle(250, 210, 30, 40, [0, 0, 0, 1]);

    parts.push(mouth);

    return parts;
}

// Mismo caso para generar la galleta
function makeCookiePivot() {
    const cookie = makeCircle(0, 0, 30, 25, [0.8, 0.6, 0.3, 1]); // centered at 0,0

    const chips = [];
    for (let i = 0; i < 6; i++) {
        const angle = Math.random() * Math.PI * 2;
        const dist  = Math.random() * 18;
        const cx = Math.cos(angle) * dist;
        const cy = Math.sin(angle) * dist;
        chips.push(makeCircle(cx, cy, 5, 10, [0.2, 0.1, 0.05, 1]));
    }

    return [cookie, ...chips];
}


// Estados globales de las transformaciones para ser avtualizados por la GUI
const objects = {
    face: {
        id: 'monster',
        t: { x: 0, y: 0 },
        s: { x: 1, y: 1 },
        r: 0
    },
    pivot: {
        pos: { x: 400, y: 200 }
    }
};

// Main that setups webgl environment
function main() {

    const canvas = document.querySelector("canvas");
    const gl = canvas.getContext("webgl2");
    twgl.resizeCanvasToDisplaySize(gl.canvas);
    gl.viewport(0,0,gl.canvas.width, gl.canvas.height);

    setupUI(gl);

    const programInfo = twgl.createProgramInfo(gl, [vsGLSL, fsGLSL]);

    // construir objetos
    const monsterParts = makeCookieMonster();
    const cookieParts  = makeCookiePivot();

    const monsterVAO = monsterParts.map(p => ({
        vao: twgl.createVAOFromBufferInfo(gl, programInfo,
              twgl.createBufferInfoFromArrays(gl,p)),
        buffer: twgl.createBufferInfoFromArrays(gl,p)
    }));

    const cookieVAO = cookieParts.map(p => ({
        vao: twgl.createVAOFromBufferInfo(gl, programInfo,
              twgl.createBufferInfoFromArrays(gl,p)),
        buffer: twgl.createBufferInfoFromArrays(gl,p)
    }));

    drawScene(gl, programInfo, monsterVAO, cookieVAO);
}

// Function to do the actual display of the objects
function drawScene(gl, programInfo, monsterParts, cookieParts) {
    gl.useProgram(programInfo.program);

    const pivot = [objects.pivot.pos.x, objects.pivot.pos.y];
    const T = objects.face; 

    // galleta con sus transformaciones independientes
    for (const p of cookieParts) {
        const matCookie = M3.translation(pivot);
        twgl.setUniforms(programInfo, {
            u_resolution: [gl.canvas.width, gl.canvas.height],
            u_transforms: matCookie
        });
        gl.bindVertexArray(p.vao);
        twgl.drawBufferInfo(gl, p.buffer);
    }

    // traslado y escala independientes de la rotaci[on en el monstruo
    for (const part of monsterParts) {
        let mat = M3.identity();

        const scale = [T.s.x, T.s.y];
        const translate = [T.t.x, T.t.y];
        const rotation = T.r;

        // Orden revisado con Lore, creditos a Lore 
        mat = M3.multiply(M3.scale(scale), mat);
        mat = M3.multiply(M3.translation(translate), mat);
        mat = M3.multiply(M3.translation([-pivot[0], -pivot[1]]), mat);
        mat = M3.multiply(M3.rotation(rotation), mat);                   
        mat = M3.multiply(M3.translation(pivot), mat);                 

        // Dibujar
        twgl.setUniforms(programInfo, {
            u_resolution: [gl.canvas.width, gl.canvas.height],
            u_transforms: mat
        });
        gl.bindVertexArray(part.vao);
        twgl.drawBufferInfo(gl, part.buffer);
    }

    requestAnimationFrame(() => drawScene(gl, programInfo, monsterParts, cookieParts));
}

// setup del GUI
function setupUI(gl) {

    const gui = new GUI();

    const tra = gui.addFolder("Move Cookie Monster");
    tra.add(objects.face.t, "x", -300, 300);
    tra.add(objects.face.t, "y", -300, 300);

    const sca = gui.addFolder("Scale Cookie Monster");
    sca.add(objects.face.s, "x", 0.3, 3);
    sca.add(objects.face.s, "y", 0.3, 3);

    gui.add(objects.face, "r", 0, Math.PI*2).name("Rotate Monster");

    const piv = gui.addFolder("Cookie Pivot Position");
    piv.add(objects.pivot.pos, "x", 0, gl.canvas.width);
    piv.add(objects.pivot.pos, "y", 0, gl.canvas.height);
}

main();


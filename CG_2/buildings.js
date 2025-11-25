/* Tarea CG 2 Amilka Daniela Lopez Aguilar A01029277 */

//El siguiente programa genera archivos OBJ a partir de numero de lados, radios de la base y cima, asi como la altura

// para manejo de archivos
import fs from 'fs'; 

function writeFile(filename, content){
    fs.writeFileSync(filename, content);
}

function getArguments(){
    const args = process.argv.slice(2); // obtenemos los argumentos

    let numLados = 8;
    let altura = 6.0;
    let radioBase = 1.0;
    let radioCima = 0.8;

    if (args[0] !== undefined) {
        const n = parseInt(args[0]);
        if (!isNaN(n) && n >= 3 && n <= 36) numLados = n;
        else console.warn("Número de lados inválido. Usando valor por defecto: 8");
    }
    if (args[1] !== undefined) {
        const h = parseFloat(args[1]);
        if (!isNaN(h) && h > 0) altura = h;
        else console.warn("Altura inválida. Usando valor por defecto: 6.0");
    }
    if (args[2] !== undefined) {
        const rBase = parseFloat(args[2]);
        if (!isNaN(rBase) && rBase > 0) radioBase = rBase;
        else console.warn("Radio de la base inválido. Usando valor por defecto: 1.0");
    }
    if (args[3] !== undefined) {
        const rCima = parseFloat(args[3]);
        if (!isNaN(rCima) && rCima > 0) radioCima = rCima;
        else console.warn("Radio de la cima inválido. Usando valor por defecto: 0.8");
    }

    return { numLados, altura, radioBase, radioCima };
}

// calcular normal de un triángulo dado 3 vértices
function calcularNormal(v1, v2, v3) { // calcular la normal del triangulo
    const u = [v2[0]-v1[0], v2[1]-v1[1], v2[2]-v1[2]]; // u va de v1 a v2
    const v = [v3[0]-v1[0], v3[1]-v1[1], v3[2]-v1[2]]; // v va de v1 a v3
// productos puntos
    const nx = u[1]*v[2] - u[2]*v[1];
    const ny = u[2]*v[0] - u[0]*v[2];
    const nz = u[0]*v[1] - u[1]*v[0];
// magnitud del vector normal
    const length = Math.sqrt(nx*nx + ny*ny + nz*nz);
// normalizar
    return [nx/length, ny/length, nz/length];
}

// calcular vertices
function generarVertices(caracteristicas){
    let [numLados, altura, radioBase, radioCima] = caracteristicas;

    const vertices = [];
    const caras = [];
    const normales = [];

    const angulo = (2 * Math.PI) / numLados;

    // crear vertices base y cima
    for (let i = 0; i < numLados; i++) {
        // generamos un circulo que sera la base con coordenadas polares
        const xBase = radioBase * Math.cos(i * angulo);
        const zBase = radioBase * Math.sin(i * angulo);
        vertices.push([xBase, 0, zBase]); // base y centramos en el plano horizontal con y = 0

        const xCima = radioCima * Math.cos(i * angulo);
        const zCima = radioCima * Math.sin(i * angulo);
        vertices.push([xCima, altura, zCima]); // cima
    }

    // caras laterales
    for (let i = 0; i < numLados; i++) {
        const next = (i + 1) % numLados; // obtener indice del siguiente vertice para cerrar poligonos
    // current vertex
        const base1 = 2 * i;
    // vertice consecutivo
        const base2 = 2 * next;
    // correspondientes a la cima, indices impares
        const top1 = 2 * i + 1;
        const top2 = 2 * next + 1;
    // vertices en sentido antihorario para que la normal apunte hacia afuera
    // Triángulo 1
        caras.push([base1, base2, top2]);
        normales.push(calcularNormal(vertices[base1], vertices[base2], vertices[top2]));
    // Triángulo 2
        caras.push([base1, top2, top1]);
        normales.push(calcularNormal(vertices[base1], vertices[top2], vertices[top1]));
    }

    // cara base (hacia abajo, sentido antihorario)
    for (let i = 1; i < numLados - 1; i++) { //cubrir todos los triangulos de la base
        caras.push([0, 2*i, 2*(i+1)]);
        normales.push([0, -1, 0]); // normal hacia abajo fija
    }

    // cara cima (hacia arriba)
    for (let i = 1; i < numLados - 1; i++) {
        caras.push([1, 2*i+1, 2*(i+1)+1]); // igual que la base pero ahora usamos los vertices de la cima
        normales.push([0, 1, 0]); // normal hacia arriba
    }

    return { vertices, caras, normales };
}

function main(){
    const args = getArguments(); //tomar los argumentos que nos paso 
    const { vertices, caras, normales } = generarVertices([args.numLados, args.altura, args.radioBase, args.radioCima]); // generamos y devolvemos a partir de los inputs: todos los vertices (xyz), caras o indices de los triangulos y sus normales

    let objData = ""; // string que sera el archivo

    // escribir vertices, uso de $ para reemplazar con el valor de las
    vertices.forEach(v => objData += `v ${v[0]} ${v[1]} ${v[2]}\n`); // v x y z y espacio

    // escribir normales
    normales.forEach(n => objData += `vn ${n[0]} ${n[1]} ${n[2]}\n`); // vn nx ny nz y espacio

    // escribir caras con referencia a normal
    caras.forEach((c, i) => {
    const f = c.map(v => `${v+1}//${i+1}`).join(" "); 
    objData += `f ${f}\n`; //para crear f 1 2 3 por ejemplo
    });

    writeFile("building.obj", objData);
    console.log("Archivo building.obj generado con éxito.");
}

main();

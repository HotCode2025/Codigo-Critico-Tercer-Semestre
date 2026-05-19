// --- CLASE PADRE: DispositivoEntrada ---
class DispositivoEntrada {
    constructor(tipoEntrada, marca) {
        this._tipoEntrada = tipoEntrada;
        this._marca = marca;
    }

    get tipoEntrada() {
        return this._tipoEntrada;
    }

    set tipoEntrada(tipoEntrada) {
        this._tipoEntrada = tipoEntrada;
    }

    get marca() {
        return this._marca;
    }

    set marca(marca) {
        this._marca = marca;
    }
}

// --- CLASE HIJA: Raton ---
class Raton extends DispositivoEntrada {
    static contadorRatones = 0;

    constructor(tipoEntrada, marca) {
        super(tipoEntrada, marca);
        this._idRaton = ++Raton.contadorRatones;
    }

    get idRaton() {
        return this._idRaton;
    }

    toString() {
        return `Ratón: [ID: ${this._idRaton}, TipoEntrada: ${this.tipoEntrada}, Marca: ${this.marca}]`;
    }
}

// --- CLASE HIJA: Teclado ---
class Teclado extends DispositivoEntrada {
    static contadorTeclados = 0;

    constructor(tipoEntrada, marca) {
        super(tipoEntrada, marca);
        this._idTeclado = ++Teclado.contadorTeclados;
    }

    get idTeclado() {
        return this._idTeclado;
    }

    toString() {
        return `Teclado: [ID: ${this._idTeclado}, TipoEntrada: ${this.tipoEntrada}, Marca: ${this.marca}]`;
    }
}

// --- CLASE INDEPENDIENTE: Monitor ---
class Monitor {
    static contadorMonitores = 0;

    constructor(marca, tamanio) {
        this._idMonitor = ++Monitor.contadorMonitores;
        this._marca = marca;
        this._tamanio = tamanio;
    }

    get idMonitor() {
        return this._idMonitor;
    }

    get marca() {
        return this._marca;
    }

    set marca(marca) {
        this._marca = marca;
    }

    get tamanio() {
        return this._tamanio;
    }

    set tamanio(tamanio) {
        this._tamanio = tamanio;
    }

    toString() {
        return `Monitor: [ID: ${this._idMonitor}, Marca: ${this.marca}, Tamaño: ${this.tamanio}]`;
    }
}

// --- CLASE QUE AGREGA COMPONENTES: Computadora ---
class Computadora {
    static contadorComputadoras = 0;

    constructor(nombre, monitor, teclado, raton) {
        this._idComputadora = ++Computadora.contadorComputadoras;
        this._nombre = nombre;
        this._monitor = monitor;
        this._teclado = teclado;
        this._raton = raton;
    }

    toString() {
        return `Computadora ${this._idComputadora}: ${this._nombre} \n   ${this._monitor} \n   ${this._teclado} \n   ${this._raton}`;
    }
}

// --- CLASE FINAL: Orden ---
class Orden {
    static contadorOrdenes = 0;

    constructor() {
        this._idOrden = ++Orden.contadorOrdenes;
        this._computadoras = [];
    }

    agregarComputadora(computadora) {
        this._computadoras.push(computadora);
    }

    mostrarOrden() {
        let computadorasOrden = '';
        for (let computadora of this._computadoras) {
            computadorasOrden += `\n ${computadora.toString()}`;
        }
        console.log(`\n=== ORDEN N° ${this._idOrden} ===`);
        console.log(`Computadoras en la orden: ${computadorasOrden}`);
    }
}

// ==========================================
// ZONA DE PRUEBAS (Creación de objetos)
// ==========================================

console.log("--- CREANDO COMPONENTES ---");
let raton1 = new Raton('USB', 'HP');
let raton2 = new Raton('Bluetooth', 'Logitech');

let teclado1 = new Teclado('USB', 'Dell');
let teclado2 = new Teclado('Bluetooth', 'Corsair');

let monitor1 = new Monitor('Samsung', '27 pulgadas');
let monitor2 = new Monitor('Dell', '24 pulgadas');

console.log(raton1.toString());
console.log(teclado1.toString());
console.log(monitor1.toString());

console.log("\n--- ENSAMBLANDO COMPUTADORAS ---");
let computadora1 = new Computadora('PC Oficina', monitor1, teclado1, raton1);
let computadora2 = new Computadora('PC Gaming', monitor2, teclado2, raton2);

console.log(computadora1.toString());

console.log("\n--- GENERANDO ORDENES ---");
let orden1 = new Orden();
orden1.agregarComputadora(computadora1);
orden1.agregarComputadora(computadora2);
orden1.mostrarOrden();

let orden2 = new Orden();
orden2.agregarComputadora(computadora2); // Agregando solo una a la orden 2
orden2.mostrarOrden();
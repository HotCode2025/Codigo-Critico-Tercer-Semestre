// --- CLASE PADRE: DispositivoEntrada ---
<<<<<<< HEAD
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
=======
// En el diagrama UML, tiene una relación de Herencia (la flecha blanca que apunta hacia arriba)
//Clase DispositivoEntrada: Es la clase Padre. Define los atributos comunes para cualquier periférico: tipoEntrada (ej. USB) y marca
//El uso del guion bajo (_) es una convención en JavaScript para indicar que estas propiedades son "privadas" (o protegidas). 
class DispositivoEntrada {
    constructor(tipoEntrada, marca) { //se ejecuta automáticamente cuando haces un new DispositivoEntrada(...)
        this._tipoEntrada = tipoEntrada; // Asigna el valor recibido a la propiedad interna _tipoEntrada
        this._marca = marca; // Asigna el valor recibido a la propiedad interna _marca
    }

    get tipoEntrada() { //Permite leer el valor de la propiedad de forma segura
        return this._tipoEntrada;
    }

    set tipoEntrada(tipoEntrada) { //Permite cambiar el valor. La ventaja de usar un set es que se puede añadir validaciones
        this._tipoEntrada = tipoEntrada;
    }

    get marca() { //Función para "leer" el dato
        return this._marca;
    }

    set marca(marca) { //Función para escribir o actualizar el dato.
>>>>>>> 32ef831070cc4bb2bb2ce2f69ef76b59add988ed
        this._marca = marca;
    }
}

// --- CLASE HIJA: Raton ---
<<<<<<< HEAD
class Raton extends DispositivoEntrada {
    static contadorRatones = 0;

    constructor(tipoEntrada, marca) {
        super(tipoEntrada, marca);
        this._idRaton = ++Raton.contadorRatones;
=======
//Clases Raton y Teclado: Son las clases Hijas. Usan extends para heredar de la clase padre.
class Raton extends DispositivoEntrada {
    static contadorRatones = 0; // Contadores Estáticos: Cada clase lo tiene y sirve para asignar un ID único a cada objeto, tal como se indica en las responsabilidades del UML.

    constructor(tipoEntrada, marca) {
        super(tipoEntrada, marca); //Llama al constructor de la clase padre para que ella se encargue de inicializar tipoEntrada y marca
        this._idRaton = ++Raton.contadorRatones; //Primero incrementa el contador y luego lo asigna a _idRaton. Esto garantiza que cada ratón tenga un ID único
>>>>>>> 32ef831070cc4bb2bb2ce2f69ef76b59add988ed
    }

    get idRaton() {
        return this._idRaton;
    }

<<<<<<< HEAD
    toString() {
=======
    toString() { //Sirve para que, cuando quiera imprimir el objeto (con un console.log), se muestre un texto legible y ordenado en lugar de un simple
>>>>>>> 32ef831070cc4bb2bb2ce2f69ef76b59add988ed
        return `Ratón: [ID: ${this._idRaton}, TipoEntrada: ${this.tipoEntrada}, Marca: ${this.marca}]`;
    }
}

// --- CLASE HIJA: Teclado ---
<<<<<<< HEAD
class Teclado extends DispositivoEntrada {
    static contadorTeclados = 0;

    constructor(tipoEntrada, marca) {
        super(tipoEntrada, marca);
        this._idTeclado = ++Teclado.contadorTeclados;
=======
// Clases Raton y Teclado: Son las clases Hijas. Usan extends para heredar de la clase padre.
//Crea una nueva clase llamada Teclado, pero asegúrate de que tenga todo lo que tiene DispositivoEntrada" (es decir, la marca y el tipo de entrada
class Teclado extends DispositivoEntrada {
    static contadorTeclados = 0; //La palabra static hace que la variable pertenezca a la clase y no a los objetos, solo existe un contadorTeclados en la memoria que va subiendo

    constructor(tipoEntrada, marca) {
        super(tipoEntrada, marca); // Envía los datos al padre
        this._idTeclado = ++Teclado.contadorTeclados; // Asigna un ID propio
>>>>>>> 32ef831070cc4bb2bb2ce2f69ef76b59add988ed
    }

    get idTeclado() {
        return this._idTeclado;
    }

<<<<<<< HEAD
    toString() {
=======
    toString() { //se muestra el objeto cuando lo convierto a texto
>>>>>>> 32ef831070cc4bb2bb2ce2f69ef76b59add988ed
        return `Teclado: [ID: ${this._idTeclado}, TipoEntrada: ${this.tipoEntrada}, Marca: ${this.marca}]`;
    }
}

// --- CLASE INDEPENDIENTE: Monitor ---
<<<<<<< HEAD
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
=======
//el Monitor NO hereda de DispositivoEntrada en el UML. Es una clase autónoma que tiene sus propios atributos: marca y tamanio, además de su propio contador de IDs.
class Monitor {
    static contadorMonitores = 0; // Variable estática: cuenta cuántos monitores se han creado

    constructor(marca, tamanio) {
        this._idMonitor = ++Monitor.contadorMonitores; // Se incrementa el contador y se asigna como ID único
        this._marca = marca; // Se asigna la marca del monitor
        this._tamanio = tamanio; // Se asigna el tamaño del monitor
    }

    get idMonitor() {
        return this._idMonitor; // Devuelve el ID del monitor (solo lectura)
    }

    get marca() {
        return this._marca; // Devuelve la marca
    }

    set marca(marca) {
        this._marca = marca; // Permite cambiar la marca
    }

    get tamanio() { 
        return this._tamanio; // Devuelve el tamaño
    }

    set tamanio(tamanio) {
        this._tamanio = tamanio; // Permite cambiar el tamaño
    }

    toString() { // Devuelve una representación en texto del objeto
>>>>>>> 32ef831070cc4bb2bb2ce2f69ef76b59add988ed
        return `Monitor: [ID: ${this._idMonitor}, Marca: ${this.marca}, Tamaño: ${this.tamanio}]`;
    }
}

// --- CLASE QUE AGREGA COMPONENTES: Computadora ---
<<<<<<< HEAD
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
=======
//En el UML, la clase Computadora tiene un rombo vacío conectado a Monitor, Ratón y Teclado. Esto es AGREGACIÒN
// Esta clase representa una computadora compuesta por varios dispositivos
class Computadora {
    static contadorComputadoras = 0; // Variable estática que lleva el conteo de computadoras creadas

    constructor(nombre, monitor, teclado, raton) {
        this._idComputadora = ++Computadora.contadorComputadoras; // Se incrementa el contador y se asigna un ID único
        this._nombre = nombre; // Nombre de la computadora (ej: "PC Gamer")
        this._monitor = monitor; // Objeto tipo Monitor asociado a la computadora
        this._teclado = teclado; // Objeto tipo Teclado asociado a la computadora
        this._raton = raton;  // Objeto tipo Ratón asociado a la computadora
    }

    toString() {  // Devuelve una representación en texto de la computadora con todos sus componentes
>>>>>>> 32ef831070cc4bb2bb2ce2f69ef76b59add988ed
        return `Computadora ${this._idComputadora}: ${this._nombre} \n   ${this._monitor} \n   ${this._teclado} \n   ${this._raton}`;
    }
}

// --- CLASE FINAL: Orden ---
<<<<<<< HEAD
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
=======
//En el UML se ve una relación con un rombo hacia Computadora.
//El Arreglo _computadoras: Es una lista vacía donde vas guardando todas las PCs que el cliente quiera comprar.
class Orden {
    static contadorOrdenes = 0; // Variable estática: lleva el conteo de órdenes creadas

    constructor() {
        this._idOrden = ++Orden.contadorOrdenes; // Se incrementa el contador y se asigna un ID único a la orden
        this._computadoras = []; // Se crea un arreglo vacío donde se almacenarán las computadoras
    }

    agregarComputadora(computadora) { 
        this._computadoras.push(computadora); // Agrega una computadora al arreglo usando push(). PUSH sirve para agregar un elemento al final de un arreglo
    }

    mostrarOrden() {
        let computadorasOrden = ''; // Variable para acumular el texto de las computadoras
        for (let computadora of this._computadoras) {  // Recorre cada computadora dentro del arreglo
            computadorasOrden += `\n ${computadora.toString()}`; // Se concatena cada computadora en formato texto (usa su método toString)
        }
        console.log(`\n=== ORDEN N° ${this._idOrden} ===`); // Muestra el ID de la orden
        console.log(`Computadoras en la orden: ${computadorasOrden}`); // Muestra todas las computadoras agregadas a la orden
>>>>>>> 32ef831070cc4bb2bb2ce2f69ef76b59add988ed
    }
}

// ==========================================
// ZONA DE PRUEBAS (Creación de objetos)
// ==========================================

console.log("--- CREANDO COMPONENTES ---");
<<<<<<< HEAD
let raton1 = new Raton('USB', 'HP');
let raton2 = new Raton('Bluetooth', 'Logitech');

let teclado1 = new Teclado('USB', 'Dell');
let teclado2 = new Teclado('Bluetooth', 'Corsair');

let monitor1 = new Monitor('Samsung', '27 pulgadas');
let monitor2 = new Monitor('Dell', '24 pulgadas');

=======
// Se crean instancias de la clase Raton (Tipo de entrada, Marca)
let raton1 = new Raton('USB', 'HP');
let raton2 = new Raton('Bluetooth', 'Logitech');

// Se crean instancias de la clase Teclado (Tipo de entrada, Marca)
let teclado1 = new Teclado('USB', 'Dell');
let teclado2 = new Teclado('Bluetooth', 'Corsair');

// Se crean instancias de la clase Monitor (Marca, Tamaño)
let monitor1 = new Monitor('Samsung', '27 pulgadas');
let monitor2 = new Monitor('Dell', '24 pulgadas');

// Se mandan a imprimir usando el método toString() definido en sus clases
>>>>>>> 32ef831070cc4bb2bb2ce2f69ef76b59add988ed
console.log(raton1.toString());
console.log(teclado1.toString());
console.log(monitor1.toString());

<<<<<<< HEAD
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
=======

//La clase Computadora recibe los objetos creados anteriormente como argumentos en su constructor (Agregacion)
console.log("\n--- ENSAMBLANDO COMPUTADORAS ---");
// Se crea la computadora 1 pasando el nombre y los 3 objetos periféricos creados arriba
let computadora1 = new Computadora('PC Oficina', monitor1, teclado1, raton1);
// Se crea la computadora 2 con una configuración distinta
let computadora2 = new Computadora('PC Gaming', monitor2, teclado2, raton2);

// Muestra el detalle completo de la computadora (incluyendo sus componentes internos)
console.log(computadora1.toString());

console.log("\n--- GENERANDO ORDENES ---");
// Se crea la primera orden (esta clase suele tener un contador de ID interno)
let orden1 = new Orden();
// Se añaden las computadoras al arreglo interno de la orden mediante un método
orden1.agregarComputadora(computadora1);
orden1.agregarComputadora(computadora2);
// Imprime el ticket de la orden con el ID y la lista de equipos
orden1.mostrarOrden();

// Se crea una segunda orden independiente
let orden2 = new Orden();
orden2.agregarComputadora(computadora2); // Solo contiene la PC Gaming
orden2.mostrarOrden(); // Para ver la Orden N° 2
>>>>>>> 32ef831070cc4bb2bb2ce2f69ef76b59add988ed

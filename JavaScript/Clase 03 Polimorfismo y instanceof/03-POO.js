class Empleado{ 
    constructor(nombre, sueldo){
        this._nombre = nombre;
        this ._sueldo = sueldo;
    }
    obtenerDetalles(){
        return `Empleado: nombre: ${this._nombre},
        Sueldo: ${this._sueldo}`;
    }
}

class Gerente extends Empleado{
    constructor(nombre, sueldo, departamento){
        super(nombre, sueldo);
        this._departamento = departamento;
    }

    //Agregamos la Sobreescritura
    obtenerDetalles(){
        return `Gerente: ${super.obtenerDetalles()} departamento: this ${this._departamento}`;
    
    }
}

//POLIFORMISMO UNA SOLA LINEA DE CODIGA EN EL METODO IMPIRMIR EJECUTA EL METODO DE LA CLASE PADRE O HIJA. MULTIPLES FORMAS EN TIEMPOS DE EJECUCION
function imprimir( tipo ){ // Recibe una variable
    console.log(tipo.obtenerDetalles() ); // Segun el tipo que le pasemos, será la información.
    if(tipo instanceof Gerente){
        console.log('Es un objeto de tipo Gerente');
        console.log(tipo._departamento) //No existe en la clase padre. 
    }
    // else if (tipo instanceof Empleado){
    //     console.log('Es de tipo Empleado');
    // }
    else if(tipo instanceof Object){ //El orden siempre es jerarquico
        console.log('Es de tipo Object'); // Clase padre de todas las clases
    }
}

let gerente1 = new Gerente("Carlos", 5000, "sistemas");
console.log(gerente1); //Objeto de la clase hija

let empleado1 = new Empleado("Juan", 3000);
console.log(empleado1); //Objeto de la clase padre

imprimir(gerente1); //En el poliformismo esta llamando al método de la clase padre
imprimir(empleado1); // Esta llamando al método de la clase hija

//Son las multiples formas en tiempo de ejecucion del poliformismo.

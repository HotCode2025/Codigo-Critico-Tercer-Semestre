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
function imprimir( tipo ){
    console.log(tipo.obtenerDetalles() );
}

let gerente1 = new Gerente("Carlos", 5000, "sistemas");
console.log(gerente1); //Objeto de la clase hija

let empleado1 = new Empleado("Juan", 3000);
console.log(empleado1); //Objeto de la clase padre

imprimir(gerente1);
imprimir(empleado1);
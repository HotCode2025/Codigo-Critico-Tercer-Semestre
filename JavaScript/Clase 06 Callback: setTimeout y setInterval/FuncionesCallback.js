mifuncion1()  // hosting llamamos la funcion antes de ser definida.
mifuncion2()

function mifuncion1(){
    console.log('Función 1')
}

function mifuncion2(){
    console.log('Funcion 2')
}

// Funcion de tipo callback

function imprimir(mensaje){
    console.log(mensaje);
}

function sumar(op1, op2, funcionCallBack){
    let res = op1 + op2;
    funcionCallBack(`Resultado: ${res}`);
}
//funcion callback establece un nuevo flujo hace un proceso por separado. Procesos asincronos.
sumar(5, 3, imprimir);


//LLAMADAS ASINCRONAS CON USO DE setTimeout

function mifuncionCallBack(){
    console.log('Saludo asincrono despues de 3 segundos');
}

setTimeout(mifuncionCallBack, 3000); 

setTimeout(function() {console.log('Saludo asincrono 2')}, 4000);

setTimeout(() => console.log('Saludo asincrono 3'), 5000);

let reloj = () => {
    let fecha = new Date();
    console.log(`${fecha.getHours()}:${fecha.getMinutes()}:${fecha.getSeconds()}`);
}

setInterval(reloj, 1000); //Cada 1 segundo se ejecuta



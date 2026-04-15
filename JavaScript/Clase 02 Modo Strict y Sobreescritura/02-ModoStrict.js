"use Strict";  //se usa al inicio del programa
 
const x = 10;
console.log(x)

miFuncion();

function miFuncion(){
   // "use strict" No permite el uso de ninguna variable sin declarar
    y = 10; 
    console.log(y)
}
miFuncion();
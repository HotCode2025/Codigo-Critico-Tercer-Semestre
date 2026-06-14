let miPromesa = new Promise((resolver, rechazar) => {
    let exprpersion = true;
    if(exprpersion){
        resolver('Resolvió correctamente');
    } else {
        rechazar('Se produjo un error');
    }
});

// miPromesa.then(
//    valor => console.log(valor),
//    error => console.log(error)
//);

//miPromesa
//   .then( valor => console.log(valor))
//    .catch(error => console.log(error));

let promesa = new Promise ((resolver) => {
    console.log('Inicio Promesa');
    setTimeout( () => resolver('Saludos desde promesa, callback, funcion flecha y setTimeout'),3000);
    console.log('Final Promesa');
});

//El llamado a la promesa
promesa.then(valor => console.log(valor));
let miPromesa = new Promise((resolver, rechazar) => {
    let exprpersion = true;
    if(exprpersion){
        resolver('Resolvió correctamente');
    } else {
        rechazar('Se produjo un error');
    }
});

miPromesa.then(
    valor => console.log(valor),
    error => console.log(error)
)
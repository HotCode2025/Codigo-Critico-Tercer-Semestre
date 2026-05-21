function seleccionarPersonajeJugador(){
// 1. Traemos los elementos del HTML a través de su ID
    let inputZuko = document.getElementById('zuko');
    let inputKatara = document.getElementById('katara');
    let inputAang = document.getElementById('aang');
    let inputToph = document.getElementById('toph');

    // 2. Evaluamos cuál de ellos tiene la propiedad 'checked' en true
    if (inputZuko.checked) {
        alert('SELECCIONASTE A ZUKO 🔥');
    } else if (inputKatara.checked) {
        alert('SELECCIONASTE A KATARA 💧');
    } else if (inputAang.checked) {
        alert('SELECCIONASTE A AANG 🌪️');
    } else if (inputToph.checked) {
        alert('SELECCIONASTE A TOPH 🌱');
    } else {
        // Es una buena práctica agregar un mensaje por si el usuario toca el botón sin elegir nada
        alert('¡POR FAVOR SELECCIONA UN PERSONAJE!'); 
    }
}
let botonPersonajeJugador = document.getElementById('boton-personaje');
botonPersonajeJugador.addEventListener('click', seleccionarPersonajeJugador);

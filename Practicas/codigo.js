// FUNCION PROPUESTA TAREA.
function aleatorio(min, max) { 
    return Math.floor(Math.random() * (max - min + 1) + min)
}

function eleccion(jugada) {
    let resultado = ""
    if (jugada == 1) {
        resultado = "Piedra 🪨"
    } else if (jugada == 2) {
        resultado = "Papel 📄"
    } else if (jugada == 3) {
        resultado = "Tijera ✂️"
    } else {
        resultado = "Mal elegido"
    }
    return resultado
}

// Inicialización de variables (corregidas a plural para coincidir con el resto del código)
let jugador = 0
let pc = 0
let triunfos = 0
let perdidas = 0

// El ciclo debe envolver todo el proceso de juego
while (triunfos < 3 && perdidas < 3) {
    pc = aleatorio(1, 3)
    jugador = prompt("Elige: 1 piedra, 2 papel, 3 tijera")

    // SEGUNDO: Mostrar elecciones
    alert("PC elige: " + eleccion(pc))
    alert("Tu eliges: " + eleccion(jugador))

    // CUARTO: Combate final (dentro del while para que sume los puntos)
    if (pc == jugador) {
        alert("EMPATE!!!")
    } else if ((jugador == 1 && pc == 3) || (jugador == 2 && pc == 1) || (jugador == 3 && pc == 2)) {
        alert("GANASTE!!!")
        triunfos = triunfos + 1
    } else {
        alert("PERDISTE!!!")
        perdidas = perdidas + 1
    }

    // Mostrar marcador actual
    alert("Ganaste " + triunfos + " veces. Perdiste " + perdidas + " veces.")
}

alert("Fin del juego. Resultado final - Ganaste: " + triunfos + " Perdiste: " + perdidas)
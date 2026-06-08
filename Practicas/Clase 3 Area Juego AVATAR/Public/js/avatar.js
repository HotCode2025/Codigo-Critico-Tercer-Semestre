window.addEventListener('load', iniciarJuego)

// Variables globales
let ataqueJugador
let ataqueEnemigo
let vidasJugador = 3
let vidasEnemigo = 3

function iniciarJuego() {
    let botonPersonajeJugador = document.getElementById('boton-personaje')

    let botonPunio = document.getElementById('boton-punio') 
    botonPunio.addEventListener('click', ataquePunio)
    
    let botonPatada = document.getElementById('boton-patada')
    botonPatada.addEventListener('click', ataquePatada)
    
    let botonBarrida = document.getElementById('boton-barrida')
    botonBarrida.addEventListener('click', ataqueBarrida)
    
    botonPersonajeJugador.addEventListener('click', seleccionarPersonajeJugador)

    let botonReiniciar = document.getElementById('boton-reiniciar')
    botonReiniciar.addEventListener('click', reiniciarJuego)
}

function seleccionarPersonajeJugador() {
    let inputZuko = document.getElementById('zuko')
    let inputKatara = document.getElementById('katara')
    let inputAang = document.getElementById('aang')
    let inputToph = document.getElementById('toph')
    
    let spanPersonajeJugador = document.getElementById('personaje-jugador')

    if (inputZuko.checked) {
        spanPersonajeJugador.innerHTML = 'Zuko'
    } else if (inputKatara.checked) {
        spanPersonajeJugador.innerHTML = 'Katara'
    } else if (inputAang.checked) {
        spanPersonajeJugador.innerHTML = 'Aang'
    } else if (inputToph.checked) {
        spanPersonajeJugador.innerHTML = 'Toph'
    } else {
        alert('Por favor, selecciona un personaje primero.')
        return 
    }

    seleccionarPersonajeEnemigo()
}

function seleccionarPersonajeEnemigo() {
    let spanPersonajeEnemigo = document.getElementById('personaje-enemigo')
    let nombreJugador = document.getElementById('personaje-jugador').innerHTML
    let personajeGenerado = ''

    do {
        let personajeAleatorio = aleatorio(1, 4)
        
        if (personajeAleatorio == 1) {
            personajeGenerado = 'Zuko'
        } else if (personajeAleatorio == 2) {
            personajeGenerado = 'Katara'
        } else if (personajeAleatorio == 3) {
            personajeGenerado = 'Aang'
        } else if (personajeAleatorio == 4) {
            personajeGenerado = 'Toph'
        }
        
    } while (personajeGenerado === nombreJugador) 

    spanPersonajeEnemigo.innerHTML = personajeGenerado
}

function ataquePunio(){ 
    ataqueJugador = 'Puño'
    ataqueAleatorioEnemigo()
}

function ataquePatada(){ 
    ataqueJugador = 'Patada'
    ataqueAleatorioEnemigo()
}

function ataqueBarrida(){ 
    ataqueJugador = 'Barrida'
    ataqueAleatorioEnemigo()
}

function ataqueAleatorioEnemigo(){ 
    let ataqueAleatorio = aleatorio(1, 3)

    if(ataqueAleatorio == 1){
        ataqueEnemigo = 'Puño'
    } else if(ataqueAleatorio == 2){
        ataqueEnemigo = 'Patada'
    } else {
        ataqueEnemigo = 'Barrida'
    }
    
    combate()
}

function combate() {
    let spanVidasJugador = document.getElementById('vidas-jugador')
    let spanVidasEnemigo = document.getElementById('vidas-enemigo')
    let resultado;

    // Lógica para determinar el ganador y restar vidas
    if (ataqueJugador == ataqueEnemigo) {
        resultado = "EMPATE"
    } else if (ataqueJugador == 'Puño' && ataqueEnemigo == 'Barrida') {
        resultado = "GANASTE"
        vidasEnemigo-- 
        spanVidasEnemigo.innerHTML = vidasEnemigo 
    } else if (ataqueJugador == 'Patada' && ataqueEnemigo == 'Puño') {
        resultado = "GANASTE"
        vidasEnemigo--
        spanVidasEnemigo.innerHTML = vidasEnemigo
    } else if (ataqueJugador == 'Barrida' && ataqueEnemigo == 'Patada') {
        resultado = "GANASTE"
        vidasEnemigo--
        spanVidasEnemigo.innerHTML = vidasEnemigo
    } else {
        resultado = "PERDISTE"
        vidasJugador-- 
        spanVidasJugador.innerHTML = vidasJugador 
    }

    crearMensaje(resultado)
    revisarVidas()
}

function revisarVidas() {
    if (vidasEnemigo == 0) {
        crearMensajeFinal("¡FELICITACIONES! Ganaste el combate 🏆")
    } else if (vidasJugador == 0) {
        crearMensajeFinal("Lo siento, perdiste el combate 😢")
    }
}

function crearMensaje(resultado){
    let sectionMensaje = document.getElementById('mensajes') 
    let parrafo = document.createElement('p')

    parrafo.innerHTML = 'Tu personaje atacó con <strong>' + ataqueJugador +  '</strong>, el personaje del enemigo atacó con <strong>' + ataqueEnemigo + '</strong> - ' + resultado

    sectionMensaje.appendChild(parrafo)
}

function crearMensajeFinal(resultadoFinal) {
    let sectionMensaje = document.getElementById('mensajes') 
    let parrafo = document.createElement('p')
    
    parrafo.innerHTML = '<strong>' + resultadoFinal + '</strong>'
    parrafo.style.backgroundColor = "#fff3cd"
    parrafo.style.color = "#856404"
    parrafo.style.textAlign = "center"
    parrafo.style.fontSize = "1.2rem"

    sectionMensaje.appendChild(parrafo)

    // Bloqueamos los botones de ataque
    let botonPunio = document.getElementById('boton-punio') 
    let botonPatada = document.getElementById('boton-patada')
    let botonBarrida = document.getElementById('boton-barrida')
    
    botonPunio.disabled = true
    botonPatada.disabled = true
    botonBarrida.disabled = true
}

function aleatorio(min, max) {
    return Math.floor(Math.random() * (max - min + 1) + min) 
}

function reiniciarJuego() {
    location.reload()
}
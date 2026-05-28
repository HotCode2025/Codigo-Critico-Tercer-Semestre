// Le digo al navegador que espere a que cargue todo el HTML antes de arrancar el juego. 
// Así me aseguro de que todos los elementos existan cuando los vaya a buscar.
window.addEventListener('load', iniciarJuego)

function iniciarJuego() {
    // Capturo el botón de seleccionar personaje que está en mi HTML
    let botonPersonajeJugador = document.getElementById('boton-personaje')
    
    // Le agrego un "escuchador de eventos" para que, cuando le haga click, dispare la función de selección
    botonPersonajeJugador.addEventListener('click', seleccionarPersonajeJugador)
}

function seleccionarPersonajeJugador() {
    // Me traigo todos los inputs de los personajes desde el HTML
    let inputZuko = document.getElementById('zuko')
    let inputKatara = document.getElementById('katara')
    let inputAang = document.getElementById('aang')
    let inputToph = document.getElementById('toph')
    
    // Acá es donde voy a inyectar el nombre del personaje que elegí para que se vea en pantalla
    let spanPersonajeJugador = document.getElementById('personaje-jugador')

    // Me fijo cuál de todos los inputs está marcado (.checked)
    if (inputZuko.checked) {
        spanPersonajeJugador.innerHTML = 'Zuko'
    } else if (inputKatara.checked) {
        spanPersonajeJugador.innerHTML = 'Katara'
    } else if (inputAang.checked) {
        spanPersonajeJugador.innerHTML = 'Aang'
    } else if (inputToph.checked) {
        spanPersonajeJugador.innerHTML = 'Toph'
    } else {
        // Si no elegí ninguno y toqué el botón, tiro una alerta para avisarme
        alert('Por favor, selecciona un personaje primero.')
        // Uso return para cortar la ejecución acá y que no siga de largo sin personaje
        return 
    }

    // Una vez que ya elegí mi personaje con éxito, llamo a la función para que la compu elija el suyo
    seleccionarPersonajeEnemigo()
}

function seleccionarPersonajeEnemigo() {
    // Busco el lugar en el HTML donde voy a mostrar al enemigo
    let spanPersonajeEnemigo = document.getElementById('personaje-enemigo')
    
    // Capturo el nombre del personaje que el jugador ACABA de elegir para poder compararlo
    let nombreJugador = document.getElementById('personaje-jugador').innerHTML
    
    // Creo una variable vacía para guardar temporalmente el personaje de la compu
    let personajeGenerado = ''

    // Uso el bucle "do...while" para que elija un personaje.
    // Si elige el mismo que el jugador, el bucle se repite y vuelve a tirar el dado.
    do {
        // Genero un número al azar entre el 1 y el 4 usando mi función ayudante
        let personajeAleatorio = aleatorio(1, 4)
        
        // Dependiendo del número que tocó, le asigno un personaje a la variable temporal
        if (personajeAleatorio == 1) {
            personajeGenerado = 'Zuko'
        } else if (personajeAleatorio == 2) {
            personajeGenerado = 'Katara'
        } else if (personajeAleatorio == 3) {
            personajeGenerado = 'Aang'
        } else if (personajeAleatorio == 4) {
            personajeGenerado = 'Toph'
        }
        
    //  MIENTRAS el personaje de la compu sea IGUAL al del jugador, repite todo.
    } while (personajeGenerado === nombreJugador) 

    // Una vez que sale del bucle, es porque encontró uno distinto. 
    spanPersonajeEnemigo.innerHTML = personajeGenerado
}

// Esta es mi función ayudante para sacar números aleatorios. 
// Le paso un mínimo y un máximo, y hace la matemática necesaria para devolverme un número entero.
function aleatorio(min, max) {
    return Math.floor(Math.random() * (max - min + 1) + min) 
}
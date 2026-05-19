let triunfos = 0; // Contador de rondas ganadas PUNTOS DEL JUGADOR
let perdidas = 0; // Contador de rondas perdidas PUNTOS DE LA PC
let p1HP = 100; // Vida del Jugador 1 (Porcentaje)
let p2HP = 100; // Vida del Jugador 2 (PC)
const DANIO = 34; // DAÑO Cuánta vida se resta por cada golpe (aprox. 3 golpes para ganar)
let music; // Referencia al elemento de audio
let musicStarted = false; // Control para no duplicar la música

window.onload = () => { //Cuando la página termina de cargar, busca el elemento de música en el HTML y le baja el volumen al 5%.
    music = document.getElementById('bg-music');
    music.volume = 0.04; 
};

function aleatorio(min, max) { //Una función matemática para generar un número al azar entre 1 y 3 (usada para la jugada del PC).
    return Math.floor(Math.random() * (max - min + 1) + min);
}

function eleccion(jugada) { //Un "traductor" que convierte los números (1, 2, 3) en texto y emojis para que el usuario los entienda.
    if (jugada == 1) return "Piedra ✊";
    if (jugada == 2) return "Papel 📄";
    if (jugada == 3) return "Tijera ✂️";
    return "";
}

function toggleMusic() { //interruptor lógico que detecta si la música está pausada para reproducirla o, de lo contrario, pausarla si ya está sonando
    if (!music) return;
    if (music.paused) {
        music.play();
        musicStarted = true;
    } else {
        music.pause();
    }
}
// Caja de Log de lo que sucede en el juego
function addLog(text, type) { //Esta función crea dinámicamente mensajes en el historial del juego
    const log = document.getElementById('log');
    const entry = document.createElement('div'); //Crea un nuevo elemento div.
    entry.innerText = `> ${text}`;
    if(type === 'win') entry.style.color = "var(--p1-color)"; //Le asigna un color dependiendo de si ganaste (verde/azul) o perdiste (rojo).
    if(type === 'lose') entry.style.color = "var(--p2-color)";
    log.prepend(entry); //Usa .prepend(entry) para que el mensaje más reciente aparezca siempre arriba de la lista.
}

function jugar(jugador) { //Es el corazón del código. Se ejecuta cuando el usuario hace clic en un botón de ataque.
    if (triunfos >= 3 || perdidas >= 3) return; //Validación: Si alguien ya llegó a 3 victorias/derrotas, la función se detiene (return).
    
    if (music && !musicStarted) { //Música: Intenta reproducir el sonido en el primer clic
        music.play().then(() => musicStarted = true).catch(() => {});
    }

    let pc = aleatorio(1, 3); //Crea una variable llamada pc y le asigna un número al azar entre 1 y 3
    document.getElementById('fx-icon').innerText = `${eleccion(jugador)} vs ${eleccion(pc)}`; 
    //document.getElementById('fx-icon').innerText - Busca en el HTML el elemento que tiene el ID "fx-icon" para cambiar el texto que tiene adentro.
    //${eleccion(jugador)} vs ${eleccion(pc)}: Es una "plantilla" que convierte los números de ambos jugadores en emojis(usando la función eleccion) para mostrar visualmente el duelo
    
    //LOGICA DEL COMBATE

    if (pc == jugador) { //Empate: Si son iguales, solo muestra el texto.
        document.getElementById('fx-text').innerText = "¡EMPATE!";
        document.getElementById('fx-text').style.color = "white";
        addLog(`EMPATE CON ${eleccion(jugador).toUpperCase()}`, "");
    } //Victoria del usuario: Evalúa las combinaciones (1 vs 3, 2 vs 1, 3 vs 2). Si se cumple, sube el contador de triunfos y resta vida al enemigo (p2HP).
    else if ((jugador == 1 && pc == 3) || (jugador == 2 && pc == 1) || (jugador == 3 && pc == 2)) {
        document.getElementById('fx-text').innerText = "¡IMPACTO!";
        document.getElementById('fx-text').style.color = "var(--p1-color)";
        triunfos++;
        p2HP -= DANIO;
        addLog(`GANASTE: ${eleccion(jugador)}`, "win");
    }
    else { // Derrota del usuario: Si no es empate ni victoria, resta vida al jugador (p1HP)
        document.getElementById('fx-text').innerText = "¡DAÑO!";
        document.getElementById('fx-text').style.color = "var(--p2-color)";
        perdidas++;
        p1HP -= DANIO;
        addLog(`PERDISTE: ${eleccion(pc)}`, "lose");
    }

    actualizarInterfaz(); //Se llama primero para que el usuario vea inmediatamente los cambios en pantalla. Por ejemplo, si recibiste un golpe, esta función es la que hace que la barra de vida se mueva y que el contador de puntos cambie de 0 a 1.
    verificarFinal(); //Se llama inmediatamente después para revisar si, tras ese último movimiento, alguien ya llegó al límite de puntos (3 triunfos o 3 pérdidas). Si se cumple, esta función "bloquea" el juego.
}

function actualizarInterfaz() { //Esta función se encarga de que lo que el usuario ve coincida con los datos internos
    let vP1 = Math.max(0, p1HP); //Usa Math.max(0, ...) para evitar que la vida muestre números negativos si el daño excede el HP restante.
    let vP2 = Math.max(0, p2HP);
    document.getElementById('p1-hp-fill').style.width = vP1 + "%"; //Calcula el ancho de las barras de vida usando el porcentaje restante.
    document.getElementById('p2-hp-fill').style.width = vP2 + "%";
    document.getElementById('p1-hp-text').innerText = vP1 + "%";
    document.getElementById('p2-hp-text').innerText = vP2 + "%";
    document.getElementById('p1-score').innerText = triunfos; // PUNTOS DEL JUGADOR Pone los triunfos del jugador en el marcador izquierdo
    document.getElementById('p2-score').innerText = perdidas; // PUNTOS DE LA PC . Pone tus derrotas en el marcador derecho
}

function verificarFinal() { //Revisa si el juego debe terminar. Si alguien llegó a 3 puntos
    if (triunfos >= 3 || perdidas >= 3) {
        const gano = triunfos >= 3;
        document.getElementById('fx-text').innerText = gano ? "¡VICTORIA!" : "¡DERROTA!"; //Muestra el mensaje de "VICTORIA" o "DERROTA
        document.getElementById('status-text').innerText = "OFFLINE"; //El sistema cambia a "OFFLINE" automáticamente cuando alguien gana o pierde 3 veces, dentro de la función verificarFinal()
        document.querySelectorAll('.btn-attack').forEach(b => b.disabled = true); //Desactiva los botones de ataque (disabled = true) para que no se pueda seguir jugando.
        document.getElementById('reset-btn').style.display = "inline-block"; //Muestra el botón de "Reiniciar".
    }
}

function reiniciarJuego() { //Restablece todas las variables a su estado original (100 HP, 0 puntos), limpia el historial de mensajes y vuelve a habilitar los botones para una nueva partida.
    triunfos = 0; perdidas = 0; p1HP = 100; p2HP = 100;
    document.getElementById('fx-text').innerText = "";
    document.getElementById('fx-icon').innerText = "";
    document.getElementById('status-text').innerText = "ONLINE"; //El juego se mantiene en "ONLINE" mientras la partida está en curso. Se restablece mediante la función reiniciarJuego()
    document.getElementById('reset-btn').style.display = "none";
    document.querySelectorAll('.btn-attack').forEach(b => b.disabled = false);
    document.getElementById('log').innerHTML = '<div>> REINICIADO...</div>';
    actualizarInterfaz();
}
let triunfos = 0;
let perdidas = 0;
let p1HP = 100;
let p2HP = 100;
const DANIO = 34;
let music;
let musicStarted = false;

window.onload = () => {
    music = document.getElementById('bg-music');
    music.volume = 0.05; 
};

function aleatorio(min, max) {
    return Math.floor(Math.random() * (max - min + 1) + min);
}

function eleccion(jugada) {
    if (jugada == 1) return "Piedra ✊";
    if (jugada == 2) return "Papel 📄";
    if (jugada == 3) return "Tijera ✂️";
    return "";
}

function toggleMusic() {
    if (!music) return;
    if (music.paused) {
        music.play();
        musicStarted = true;
    } else {
        music.pause();
    }
}

function addLog(text, type) {
    const log = document.getElementById('log');
    const entry = document.createElement('div');
    entry.innerText = `> ${text}`;
    if(type === 'win') entry.style.color = "var(--p1-color)";
    if(type === 'lose') entry.style.color = "var(--p2-color)";
    log.prepend(entry);
}

function jugar(jugador) {
    if (triunfos >= 3 || perdidas >= 3) return;
    
    if (music && !musicStarted) {
        music.play().then(() => musicStarted = true).catch(() => {});
    }

    let pc = aleatorio(1, 3);
    document.getElementById('fx-icon').innerText = `${eleccion(jugador)} vs ${eleccion(pc)}`;

    if (pc == jugador) {
        document.getElementById('fx-text').innerText = "¡EMPATE!";
        document.getElementById('fx-text').style.color = "white";
        addLog(`EMPATE CON ${eleccion(jugador).toUpperCase()}`, "");
    }
    else if ((jugador == 1 && pc == 3) || (jugador == 2 && pc == 1) || (jugador == 3 && pc == 2)) {
        document.getElementById('fx-text').innerText = "¡IMPACTO!";
        document.getElementById('fx-text').style.color = "var(--p1-color)";
        triunfos++;
        p2HP -= DANIO;
        addLog(`GANASTE: ${eleccion(jugador)}`, "win");
    }
    else {
        document.getElementById('fx-text').innerText = "¡DAÑO!";
        document.getElementById('fx-text').style.color = "var(--p2-color)";
        perdidas++;
        p1HP -= DANIO;
        addLog(`PERDISTE: ${eleccion(pc)}`, "lose");
    }

    actualizarInterfaz();
    verificarFinal();
}

function actualizarInterfaz() {
    let vP1 = Math.max(0, p1HP);
    let vP2 = Math.max(0, p2HP);
    document.getElementById('p1-hp-fill').style.width = vP1 + "%";
    document.getElementById('p2-hp-fill').style.width = vP2 + "%";
    document.getElementById('p1-hp-text').innerText = vP1 + "%";
    document.getElementById('p2-hp-text').innerText = vP2 + "%";
    document.getElementById('p1-score').innerText = triunfos;
    document.getElementById('p2-score').innerText = perdidas;
}

function verificarFinal() {
    if (triunfos >= 3 || perdidas >= 3) {
        const gano = triunfos >= 3;
        document.getElementById('fx-text').innerText = gano ? "¡VICTORIA!" : "¡DERROTA!";
        document.getElementById('status-text').innerText = "OFFLINE";
        document.querySelectorAll('.btn-attack').forEach(b => b.disabled = true);
        document.getElementById('reset-btn').style.display = "inline-block";
    }
}

function reiniciarJuego() {
    triunfos = 0; perdidas = 0; p1HP = 100; p2HP = 100;
    document.getElementById('fx-text').innerText = "";
    document.getElementById('fx-icon').innerText = "";
    document.getElementById('status-text').innerText = "ONLINE";
    document.getElementById('reset-btn').style.display = "none";
    document.querySelectorAll('.btn-attack').forEach(b => b.disabled = false);
    document.getElementById('log').innerHTML = '<div>> REINICIADO...</div>';
    actualizarInterfaz();
}
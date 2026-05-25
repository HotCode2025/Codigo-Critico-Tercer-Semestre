function actualizarReloj() {
    const ahora = new Date();
    
    // Obtener tiempo
    const h = ahora.getHours();
    const m = ahora.getMinutes();
    const s = ahora.getSeconds();

    // Obtener fecha
    const dia = ahora.getDate();
    const mesIndex = ahora.getMonth();
    const meses = ['ENE', 'FEB', 'MAR', 'ABR', 'MAY', 'JUN', 'JUL', 'AGO', 'SEP', 'OCT', 'NOV', 'DIC'];
    
    // Elementos DOM
    const agujaHora = document.getElementById('aguja-hora');
    const agujaMinuto = document.getElementById('aguja-minuto');
    const agujaSegundo = document.getElementById('aguja-segundo');
    const displayFecha = document.getElementById('fecha-digital');
    const displayAmPm = document.getElementById('am-pm');

    // Cálculos de rotación
    const hDeg = (h % 12) * 30 + (m * 0.5);
    const mDeg = m * 6 + (s * 0.1);
    const sDeg = s * 6;

    // Aplicar rotación
    agujaHora.style.transform = `translateX(-50%) rotate(${hDeg}deg)`;
    agujaMinuto.style.transform = `translateX(-50%) rotate(${mDeg}deg)`;
    agujaSegundo.style.transform = `translateX(-50%) rotate(${sDeg}deg)`;

    // Actualizar Pantalla Digital (F1 Style)
    const diaFormateado = dia < 10 ? '0' + dia : dia;
    displayFecha.textContent = `${diaFormateado} ${meses[mesIndex]}`;
    displayAmPm.textContent = h >= 12 ? 'PADDOCK PM' : 'PADDOCK AM';
}

// Actualizar cada segundo
setInterval(actualizarReloj, 1000);

// Iniciar inmediatamente
actualizarReloj();
// Captura del formulario de login usando su etiqueta nativa dentro del DOM
const formulario = document.querySelector('form');

// Escucha activa del evento 'submit' (cuando el usuario hace clic en el botón Login)
formulario.addEventListener('submit', function(evento) {
    
    // Evita el comportamiento por defecto del formulario (previene que la página se recargue)
    evento.preventDefault();
    
    // Captura los inputs de texto y contraseña basados en sus atributos de tipo
    const usuarioInput = document.querySelector('input[type="text"]');
    const passwordInput = document.querySelector('input[type="password"]');
    
    // Extracción de los valores ingresados eliminando espacios en blanco al inicio y al final (.trim)
    const usuario = usuarioInput.value.trim();
    const password = passwordInput.value.trim();
    
    // VALIDACIÓN LOCAL DE CAMPOS
    // Comprueba si alguno de los campos quedó vacío a pesar del atributo 'required' de HTML
    if (usuario === '' || password === '') {
        alert('Por favor, completa todos los campos requeridos.');
        return; // Interrumpe la ejecución del código si hay error
    }
    
    // SIMULACIÓN DE LOGEO (Hardcoded para entorno de prueba local)
    // En producción, aquí se realizaría una petición fetch/axios hacia una API o base de datos
    if (usuario === 'admin' && password === '1234') {
        
        // Mensaje temporal de éxito en consola y pantalla
        console.log('Acceso concedido para el usuario:', usuario);
        alert('¡Bienvenido! Inicio de sesión correcto.');
        
        // Aquí puedes redireccionar al usuario a la pantalla principal del sistema:
        // window.location.href = 'dashboard.html';
        
    } else {
        // Manejo de credenciales incorrectas
        alert('Usuario o contraseña incorrectos. Inténtalo de nuevo.');
        
        // Limpieza del campo de contraseña por seguridad para un nuevo intento
        passwordInput.value = '';
        passwordInput.focus(); // Devuelve el foco del teclado al campo de contraseña
    }
});
# 🌪️💧🌿🔥 Avatar: La Leyenda de Aang - Mini Juego Web

¡Hola! Este es un proyecto interactivo que desarrollamos para poner en práctica nuestros conocimientos de **HTML, CSS y JavaScript Vanilla**, enfocándonos fuertemente en la **manipulación del DOM** y el manejo de eventos en equipo.

La idea central es recrear un combate básico estilo Avatar, donde el jugador elige su personaje favorito y se enfrenta a un enemigo asignado al azar por el sistema.

El **DOM (Document Object Model)** o Modelo de Objetos del Documento, es una interfaz de programación. Cuando el navegador carga nuestro archivo HTML, crea una representación estructurada en forma de árbol con todos los elementos de la página (a los que llamamos "nodos"). 

Para nosotros, entender el DOM es fundamental porque es el puente que le permite a nuestro código JavaScript comunicarse con el HTML. Gracias al DOM, podemos indicarle al sistema que capture un botón específico, lea qué opción seleccionó el usuario y actualice los textos en la pantalla en tiempo real, todo sin necesidad de recargar la página.

## Tecnologías que implementamos

* **HTML5:** Para construir toda la estructura semántica de la interfaz (secciones, inputs tipo radio, botones).
* **CSS3:** Para darle un diseño moderno y responsivo. Utilizamos `flexbox` para la alineación de elementos, estilizamos los botones simulando tarjetas interactivas y aplicamos transiciones para los efectos visuales (`:hover` y `:active`).
* **JavaScript (Vanilla):** El núcleo lógico del juego. Decidimos no usar frameworks externos para afianzar nuestras bases en el lenguaje.
* **Phosphor Icons:** Integramos esta librería externa para sumar iconografía minimalista y mejorar la experiencia visual del usuario.

## Nuestra lógica y manejo del DOM

Para que el juego funcione de manera estructurada y libre de errores, organizamos nuestro código siguiendo estos lineamientos:

1.  **Carga Segura del Entorno:** Implementamos `window.addEventListener('load', iniciarJuego)` para garantizar que nuestro script no intente interactuar con el HTML antes de que el navegador lo haya renderizado por completo.

2.  **Captura de Elementos (Nodos):**
    A lo largo del desarrollo, utilizamos `document.getElementById()` para capturar del HTML exactamente los nodos que necesitamos en cada función: los botones de acción, los inputs para identificar la selección del usuario, y las etiquetas `<span>` que actúan como contenedores dinámicos.

3.  **Inyección de Datos y Modificación del DOM:**
    Una vez que validamos la elección del jugador (si no selecciona nada, interrumpimos el flujo con un `return` y disparamos un `alert`), usamos la propiedad `.innerHTML` para inyectar dinámicamente el nombre del personaje en la pantalla. Así, modificamos el árbol del DOM en tiempo real según la interacción.

4.  **Aleatoriedad del Enemigo:**
    Desarrollamos una función matemática reutilizable usando `Math.floor(Math.random() * (max - min + 1) + min)`. Esto nos permite generar un número entero aleatorio del 1 al 4, con el cual el sistema "decide" qué personaje enemigo asignar, plasmándolo también en la interfaz mediante el DOM.

---
*Desarrollado por el equipo **Código Crítico** - Estudiantes de Programación en UTN.*
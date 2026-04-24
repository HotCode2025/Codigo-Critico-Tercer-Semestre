package mundopc;

import ar.com.system2023.mundopc.*; //con * se importan todas las clases de ar.com.systema2023

public class mundoPC {
    public static void main(String[] args) {
        Monitor monitorHP = new Monitor("HP", 13); //Importar la Clase
        Teclado tecladoHP = new Teclado("Bluetooth", "HP");
        Raton ratonHP = new Raton("Bluetooth", "HP");
        Computadora computadoraHP = new Computadora("Computadora HP", monitorHP, tecladoHP, ratonHP); // creamos el objeto computadora
        
        //Creamos otros objetos de diferente marca
        Monitor monitorGamer = new Monitor("Gamer", 32);
        Teclado tecladoGamer = new Teclado("Bluetooth", "Gamer");
        Raton ratonGamer = new Raton("Bluetooth", "Gamer");
        Computadora computadoraGamer = new Computadora("Computadora Gamer", monitorGamer, tecladoGamer, ratonGamer); 
        
        Orden orden1 = new Orden(); //Inicializamos el arreglo vacio
        Orden orden2 = new Orden(); // Una nueva lista para el objeto orden2
        orden1.agregarComputadora(computadoraHP);
        orden1.agregarComputadora(computadoraGamer);
        orden1.motrarOrden();
        
        Computadora computadoraVarias = new Computadora("Computadora de diferentes marcas", monitorHP, tecladoGamer,ratonHP);
       orden2.agregarComputadora(computadoraVarias);
       orden2.motrarOrden();
       
       //Crear mas objetovs de tipo commputadora con todos sus elementos
       //completar una lista en el objeto orden1 que llegue a los 10 elementos
       //probar de esta manera los metodos al maximo rendimiento
       
        
            // 3. Computadora de Oficina
        Monitor monitorOficina = new Monitor("Samsung", 24);
        Teclado tecladoOficina = new Teclado("Cable", "Lenovo");
        Raton ratonOficina = new Raton("Cable", "Genius");
        Computadora compuOficina = new Computadora("PC Oficina", monitorOficina, tecladoOficina, ratonOficina);
        orden1.agregarComputadora(compuOficina);

        // 4. Computadora Mac (Simulada)
        Computadora compuMac = new Computadora("MacBook Pro", new Monitor("Retina", 15), new Teclado("Bluetooth", "Apple"), new Raton("Bluetooth", "Apple"));
        orden1.agregarComputadora(compuMac);

        // 5. PC de Diseño
        Computadora compuDiseno = new Computadora("PC Diseño", new Monitor("Dell UltraSharp", 27), new Teclado("Mecánico", "Logitech"), new Raton("Inalámbrico", "Logitech"));
        orden1.agregarComputadora(compuDiseno);

        // 6 a 10. Usando un bucle para testear el contador de IDs y el límite del arreglo
        for (int i = 6; i <= 10; i++) {
      Computadora compuTest = new Computadora("PC Test " + i, monitorHP, tecladoHP, ratonHP);
      orden1.agregarComputadora(compuTest);
        }

        // Ahora mostramos la orden completa con los 10 elementos
        System.out.println("--- MOSTRANDO ORDEN 1 COMPLETA (10 ELEMENTOS) ---");
        orden1.motrarOrden();

// PRUEBA DE RENDIMIENTO: Intentar agregar la número 11 (debería saltar tu mensaje de error/límite)
        Computadora compuExtra = new Computadora("PC Sobrante", monitorHP, tecladoHP, ratonHP);
        orden1.agregarComputadora(compuExtra);
        
    }
    
}

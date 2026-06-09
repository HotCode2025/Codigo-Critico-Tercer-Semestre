import java.util.Scanner;
public class CalculadoraUTN {
    public static void main(String[] args) {
        Scanner entrada = new Scanner(System.in);
        while (true){ // Ciclo Infinito - se termina con break
            System.out.println("******* Aplicación Calculadora *******");
            mostrarMenu();

            try {
                var operacion = Integer.parseInt(entrada.nextLine());
                // Corregido: Condición para verificar si está entre 1 y 4
                if (operacion >= 1 && operacion <= 4) {
                    ejecutarOperacion(operacion, entrada);
                } // Fin del if
                else if (operacion == 5) {
                    System.out.println("Hasta pronto...");
                    break; // Rompe el ciclo y Sale
                } else {
                    System.out.println("Opcion erronea: " + operacion);
                }
                // Imprimimos un salto de linea antes  de repetir el menú
                System.out.println();
            } catch (Exception e){ //Fin try, comienzo del catch
                System.out.println("Ocurrio un error: "+e.getMessage());
                System.out.println();
            }
        } // Fin While
    } // Fin main

    private static void mostrarMenu(){
        // Mostramos el menú
        System.out.println("""
                    1. Suma
                    2. Resta
                    3. Multiplicacion
                    4. Division
                    5. Salir
                    """);
        System.out.print("Operacion a realizar? ");
    } // Fin metodo mostrarMenu

    private static void ejecutarOperacion(int operacion, Scanner entrada){ // es static para que se pueda ejecutar dentro de metodo main
        System.out.print("Digite el valor para el operando1: ");
        var operando1 = Double.parseDouble(entrada.nextLine());
        System.out.print("Digite el valor para el operando2: ");
        var operando2 = Double.parseDouble(entrada.nextLine());
        // Declaramos la variable una sola vez
        double resultado;

        switch (operacion) {
            case 1 -> { // Suma
                resultado = operando1 + operando2;
                System.out.println("Resultado de la suma: " + resultado);
            }
            case 2 -> { // Resta
                resultado = operando1 - operando2;
                System.out.println("Resultado de la resta: " + resultado);
            }
            case 3 -> { // Multiplicacion
                resultado = operando1 * operando2;
                System.out.println("Resultado de la multiplicacion: " + resultado);
            }
            case 4 -> { // Division
                // Corregido: Cambiado * por /
                if (operando2 != 0) {
                    resultado = operando1 / operando2;
                    System.out.println("Resultado de la division: " + resultado);
                } else {
                    System.out.println("Error: No se puede dividir por cero.");
                }
            }
            default -> System.out.println("Opcion erronea: " + operacion);
        } // Fin del switch
    } // Fin metodo ejecutarOperacion
} // Fin clase
package test;

import static aritmetica.Aritmetica.division;
import excepciones.OperacionExcepcion;


public class TestExcepciones { // el codigo o nuestro programa sigue corriendo a pesar de un error por eso son excepciones
    public static void main(String[] args) {
       int resultado = 0;
        try{
           resultado = division(10, 0);
        } catch(OperacionExcepcion e){
            System.out.println("Oucrrio un error de tipo OperacionExcepcion");
            System.out.println(e.getMessage());
            
       }  catch(Exception e){
           System.out.println("Ocurrio un Error");
           e.printStackTrace(System.out); //Se conoce como la pila de excepciones
            System.out.println(e.getMessage());  
       }
        finally{ // siempre se ejecuta el finally si hay o no excepciones
            System.out.println("Se reviso la división entre cero");
        }
        System.out.println("La Variable de Resultado tiene como valor: "+resultado);
                    
    }
    
}

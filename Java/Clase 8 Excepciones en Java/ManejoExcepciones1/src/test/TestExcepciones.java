package test;


public class TestExcepciones { // el codigo o nuestro programa sigue corriendo a pesar de un error por eso son excepciones
    public static void main(String[] args) {
       int resultado = 0;
       // try{
                resultado = 10/0;
//       }  catch(Exception e){
//           System.out.println("Ocurrio un Error");
//           e.printStackTrace(System.out); //Se conoce como la pila de excepciones
//           
//       }
        System.out.println("La Variable de Resultado tiene como valor: "+resultado);
                    
    }
    
}

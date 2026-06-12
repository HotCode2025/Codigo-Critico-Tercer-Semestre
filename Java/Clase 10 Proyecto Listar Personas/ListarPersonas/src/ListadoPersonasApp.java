import java.util.ArrayList;
import java.util.List;
import java.util.Scanner;

public class ListadoPersonasApp {
    public static void main(String[] args) {
        Scanner entrada = new Scanner(System.in);
        //definimos la listafuera del ciclo while
        List<Persona> personas = new ArrayList<>();
        //Empezamos con el menú
        var salir = false;
        while(!salir){
            mostrarMenu();
            System.out.println();
        } //Fin del ciclo while
    } //Fin Metodo Main

    private static void mostrarMenu(){
        //Mostramos las opciones
        System.out.print("""
                ****** Listado de personas ******
                1. Agregar
                2. Listar
                3. Salir
                """);
        System.out.print("Digite una de las opciones: ");
    }

}
//
//package domain;
//
//
//public class Persona {
//    private final int idPersona;
//    private static int contadorPersonas;
//    
//   static { //BLOQUE DE INICIALIZACION ESTATICO
//       System.out.println("Ejecución del Bloque Estatico");
//       ++Persona.contadorPersonas; 
//       // idPersona = 10; No es un atributo estatico por esto tenemos un error.
//   }
//   
//   
//   { //Bloque de inicializacion NO estatico (contexto dinamico)
//       System.out.println("Ejecucion del bloque NO estatico");
//       this.idPersona = Persona.contadorPersonas++; //Incrementamos el atributo
//       
//   }
//   
//    //Los bloques de inicializacion se ejecutgan antes del constructor
//   
//   public Persona(){
//       System.out.println("Ejecucion del constructor");
//   }
//   
//   public int getidPersona(){
//       return this.idPersona;
//   }
//
//    @Override
//    public String toString() {
//        return "Persona{" + "idPersona=" + idPersona + '}';
//    }
//}

// Tarea ==>

// ********El static le pertenece a la clase (se hace una sola vez).

// ******* El no estático le pertenece al objeto (se hace cada vez que nace una "Persona"). ******

package domain;

public class Persona {

    private final int idPersona;
    // REEMPLAZO DEL BLOQUE STATIC: Inicialización directa en la declaración
    private static int contadorPersonas = 0;

    /* // BLOQUE ESTÁTICO ORIGINAL (Comentado para la tarea)
    static {
        System.out.println("Ejecución del Bloque Estático");
        ++Persona.contadorPersonas;
    }
    */

    /* // BLOQUE NO ESTÁTICO ORIGINAL (Comentado para la tarea)
    {
        System.out.println("Ejecución del bloque NO estático");
        this.idPersona = Persona.contadorPersonas++;
    }
    */

    // REEMPLAZO DEL BLOQUE NO ESTÁTICO: Lógica integrada en el constructor
    public Persona() {
        System.out.println("Ejecución del constructor (Lógica de inicialización reemplazada)");
        // Primero incrementamos el contador de la clase y luego lo asignamos al ID de la instancia
        this.idPersona = ++Persona.contadorPersonas;
    }

    public int getIdPersona() {
        return this.idPersona;
    }

    @Override
    public String toString() {
        return "Persona{" + "idPersona=" + idPersona + '}';
    }
}
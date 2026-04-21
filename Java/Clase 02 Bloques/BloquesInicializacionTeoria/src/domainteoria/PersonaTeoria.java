package domainteoria;

public class PersonaTeoria {
    private final int idPersona;
    private static int contadorPersonas;
    
    static{ //Bloque de inicializacion estatico
        System.out.println("Ejecucion de bloque estatico");
        ++PersonaTeoria.contadorPersonas;
        // idPersona = 10; NO es un atributo estatico por esto tenemos un error
        
    }
    
    { //Bloque de inicializacion NO estatico (contexto dinamico)
        System.out.println("Ejecucion del bloque NO estatico");
        this.idPersona = PersonaTeoria.contadorPersonas++; // Incrementamos el atributo 
    }
    
    //LOS BLOQUES DE INICIALIZACION SE EJECUTAN ANTES DEL CONSTRUCTOR
    
    public PersonaTeoria(){
        System.out.println("Ejecucion del constructor");
    }
    
    public int getidPersona(){
        return this.idPersona;
    }

    @Override
    public String toString() {
        return "PersonaTeoria{" + "idPersona=" + idPersona + '}';
    }
    
    
}

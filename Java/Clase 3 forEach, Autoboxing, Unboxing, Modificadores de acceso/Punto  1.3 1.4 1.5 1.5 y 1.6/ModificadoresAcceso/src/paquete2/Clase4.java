package paquete2;

public class Clase4 {
    private String atributoPrivate = "Atributo Privado";
    
    private Clase4(){
        System.out.println("Constructor Privado");
    }
    
    //Creamos un constructor public para poder crear objetos
    public Clase4(String argumento){ // Aqui se puede llamar al constructor vacio
        this();
        System.out.println("Constructor Publico");
    }
    
    //Metodo Private
    private void metodoPrivado(){
        System.out.println("Metodo Privado");
    }

    public String getAtributoPrivate() {
        return atributoPrivate;
    }

    public void setAtributoPrivate(String atributoPrivate) {
        this.atributoPrivate = atributoPrivate;
    }
    
    
}

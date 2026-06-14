package test;

public class TestAutoboxingUnboxing {
    public static void main(String[] args) {
        // Clases envolventes o Wrapper
        /*
        Clases envolventes de tipos primitivos
        int = la clase envolvente es Integer
        long = la clase envolvente es Long
        float = la calse envolvente es Float
        double = la clase envolvente es Double
        boolean = la clase envolvente es Boolean
        byte = la clase envolvente es Byte
        char = la clase envolvente es Character
        short = la clase envolvente es Short
        
        */
        
        int enteroPrim = 10; // Tipo Primivito
        
        System.out.println("enteroPrim = " + enteroPrim);
        
        Integer entero = 10; // Tipo Object con la clase Integer
        
        //System.out.println("entero = " + entero.toString()); // esto es una cadena no es el mismo resultado que arriba.
        
        System.out.println("entero = " + entero.doubleValue());  // El tipo objeto lo conventirmos al tipo primivito es el Autoboxing 
        
        int entero2 = entero; //UNBOXING lo contrario a AUTOBOXING
        System.out.println("entero2 = " + entero2);
       
    }
    
}

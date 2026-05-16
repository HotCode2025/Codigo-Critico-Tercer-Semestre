package test;

import domain.*; // * hereda todas las clases del paquete domain

public class TestConversionObjetos {
    public static void main(String[] args) {
        Empleado empleado;
        
        empleado = new Escritor("Juan", 5000, TipoEscritura.CLASICO);
        //System.out.println("empleado = " + empleado);
        System.out.println(empleado.obtenerDetalles()); //Si queremos acceder a métodos Escritor
        
        //empleado.getTipoEscritura(); NO SE PUEDE HACER
        
        //Downcasting convertimos un tipo padre a la clase hija
        //((Escritor)empleado).getTipoEscritura(); //Tenemos 2 opciones: esta es una
        Escritor escritor = (Escritor)empleado; //Esta es la segunda opción
        escritor.getTipoEscritura();
        
        //Upcasting tipo de la clase hija a un tipo de la clase padre
        Empleado empleado2 = escritor;
        System.out.println(empleado2.obtenerDetalles());
    }
}
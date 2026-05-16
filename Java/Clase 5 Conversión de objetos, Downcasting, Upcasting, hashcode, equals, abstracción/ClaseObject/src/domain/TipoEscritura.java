package domain;

public enum TipoEscritura {
    CLASICO("Escritura a mano"),
    MODERNO("Escritura digital"); // El punto y coma va solo acá, al final de la lista

    private final String descripcion;

    // Constructor
    private TipoEscritura(String descripcion) {
        this.descripcion = descripcion;
    }

    // Método GET
    public String getDescripcion() {
        return this.descripcion;
    }
}
package enumeraciones;

public enum Continentes {
    AFRICA(54, "1.4 billones"),
    EUROPA(50, "745 millones"),
    ASIA(48, "4.7 billones"),
    AMERICA(35, "1.0 billones"),
    OCEANIA(14, "45 millones");
    
    private final int paises;
    private String habitantes;
    
    Continentes(int paises, String habitantes){
        this.paises = paises;
        this.habitantes = habitantes;
    }
    
    //Metodo GET
    public int getPaises(){
        return this.paises;
    }
    
    public String getHabitantes(){
        return this.habitantes;
        
    }
    
}

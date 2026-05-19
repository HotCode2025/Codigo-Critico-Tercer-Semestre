# Archivo: dominio/pelicula.py

class Pelicula:
    # El método __init__ es el constructor. Se ejecuta al crear una nueva película.
    def __init__(self, nombre):
        # El guion bajo antes de 'nombre' (_nombre) indica que es un atributo "privado"
        # Tal como lo pide el diagrama UML con el signo menos (- nombre: str)
        self._nombre = nombre

    # Creamos un "getter" (propiedad) para poder acceder al nombre de la película desde afuera
    @property
    def nombre(self):
        return self._nombre

    # Creamos un "setter" por si necesitamos modificar el nombre de la película en el futuro
    @nombre.setter
    def nombre(self, nombre):
        self._nombre = nombre

    # El método __str__ se ejecuta automáticamente cuando intentamos imprimir el objeto con print()
    # El diagrama pide explícitamente este método (+ __str__())
    def __str__(self):
        return f'Película: {self._nombre}'
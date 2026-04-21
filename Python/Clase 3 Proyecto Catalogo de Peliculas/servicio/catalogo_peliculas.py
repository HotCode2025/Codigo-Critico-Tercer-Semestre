# Archivo: servicio/catalogo_peliculas.py
import os # Importamos os para poder eliminar el archivo físico de nuestra computadora

class CatalogoPeliculas:
    # Atributo de clase (estático). Guarda la ruta donde se guardará el archivo de texto.
    ruta_archivo = 'peliculas.txt'

    # Usamos @classmethod porque el diagrama indica que los métodos son «static»
    # En Python, @classmethod es ideal para trabajar con atributos de clase como 'ruta_archivo'
    @classmethod
    def agregar_pelicula(cls, pelicula):
        # 'a' (append) abre el archivo para agregar texto al final sin borrar lo anterior.
        # Si el archivo no existe, lo crea automáticamente.
        with open(cls.ruta_archivo, 'a', encoding='utf8') as archivo:
            # Escribimos el nombre de la película y un salto de línea (\n)
            archivo.write(f'{pelicula.nombre}\n')
        print(f'Se agregó la película: {pelicula.nombre}')

    @classmethod
    def listar_peliculas(cls):
        try:
            # 'r' (read) abre el archivo solo para lectura
            with open(cls.ruta_archivo, 'r', encoding='utf8') as archivo:
                print('\n--- Catálogo de Películas ---')
                # Imprimimos todo el contenido del archivo
                print(archivo.read())
                print('-----------------------------\n')
        except FileNotFoundError:
            # Si intentan listar pero el archivo aún no existe, atrapamos el error para que el programa no falle
            print('\nEl catálogo está vacío. Aún no se ha creado el archivo.\n')

    @classmethod
    def eliminar(cls):
        try:
            # os.remove borra el archivo físico de la computadora
            os.remove(cls.ruta_archivo)
            print(f'\nArchivo {cls.ruta_archivo} eliminado con éxito.\n')
        except FileNotFoundError:
            # Si intentan borrar un archivo que no existe, evitamos el error
            print('\nEl archivo no existe, no hay nada que eliminar.\n')
# Archivo: test_catalogo_peliculas.py

# Importamos las clases que creamos en los otros archivos
from dominio.pelicula import Pelicula
from servicio.catalogo_peliculas import CatalogoPeliculas

opcion = None

# Iniciamos un bucle while que se repetirá hasta que el usuario elija la opción 4 (Salir)
while opcion != 4:
    try:
        # Mostramos el menú que pide el diagrama UML
        print('Opciones:')
        print('1) Agregar película')
        print('2) Listar películas')
        print('3) Eliminar archivo de películas')
        print('4) Salir')

        # Pedimos al usuario que ingrese un número
        opcion = int(input('Elige una opción (1-4): '))

        # Evaluamos qué opción eligió el usuario
        if opcion == 1:
            nombre_pelicula = input('Proporciona el nombre de la película: ')
            # Creamos el objeto película con el nombre ingresado
            pelicula = Pelicula(nombre_pelicula)
            # Llamamos al método estático para guardar la película en el archivo
            CatalogoPeliculas.agregar_pelicula(pelicula)

        elif opcion == 2:
            # Llamamos al método para mostrar las películas guardadas
            CatalogoPeliculas.listar_peliculas()

        elif opcion == 3:
            # Llamamos al método que borra el archivo txt
            CatalogoPeliculas.eliminar()

        elif opcion == 4:
            print('Saliendo del programa')

        else:
            print('\nPor favor, elige una opción válida entre 1 y 4.\n')

    except Exception as e:
        # Si el usuario ingresa una letra en lugar de un número, atrapamos el error aquí
        print(f'\nOcurrió un error: {e}')
        print('Asegúrate de ingresar un número entero.\n')
        opcion = None  # Reiniciamos la opción para que el bucle vuelva a mostrar el menú
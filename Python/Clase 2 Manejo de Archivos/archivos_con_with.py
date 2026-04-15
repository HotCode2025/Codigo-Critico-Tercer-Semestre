from ManejoArchivos import ManejoArchivos

# MANEJO DE CONTEXTO WITH: sintaxis simplificada, abre y cierra el archivo
# with open('Prueba.txt', 'r', encoding='utf8') as archivo:
   #print(archivo.read())

# No hace falta ni el try, ni el finally
# en el contexto de with lo que se ejecuta de manera automatica
# Utiliza diferentes metodos: __enter__  este es el que abre
# ahora el sigueinte metodo es el que cierra:  __exit__

with ManejoArchivos('Prueba.txt') as archivo:
    print(archivo.read())
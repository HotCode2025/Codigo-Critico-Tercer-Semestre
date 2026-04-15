#Declaramos una variable
try:
    archivo = open('Prueba.txt', 'w', encoding='utf8') # La W es de WRITE que significa ESCRIBIR
    archivo.write('Programamos con diferentes tipos de archivos, ahora en txt.\n')
    archivo.write('Los acentos son importantes para las palabras\n')
    archivo.write('como por ejemplo: acción, ejecución y producción\n')
    archivo.write('Las letras son:\nr read leer, \na append anexa, \nw write escribe, \nx crea un archivo')
    archivo.write('\nt esta es para texto o text, \nb archivos binarios, \nw+ lee y escribe son iguales nr+\n')
    archivo.write('Con esto terminamos')
except Exception as e:
    print(e)
finally: #siempre se ejecuta
    archivo.close() # Con esto se debe cerrar el archivo.

# archivo.write('Todo quedo perfecto') Este es un error

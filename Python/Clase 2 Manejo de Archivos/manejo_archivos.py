#Declaramos una variable
try:
    archivo = open('Prueba.txt', 'w') # La W es de WRITE que significa ESCRIBIR
    archivo.write('Programamos con diferentes tipos de archivos, ahora en txt.\n')
    archivo.write('Con esto terminamos')
except Exception as e:
    print(e)
finally: #siempre se ejecuta
    archivo.close() # Con esto se debe cerrar el archivo.

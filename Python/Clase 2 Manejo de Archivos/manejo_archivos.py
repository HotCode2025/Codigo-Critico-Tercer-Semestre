#Declaramos una variable
try:
    archivo = open('Prueba.txt', 'w') # La W es de WRITE que significa ESCRIBIR
except Exception as e:
    print(e)
finally: #siempre se ejecuta
    archivo.close() # Con esto se debe cerrar el archivo.

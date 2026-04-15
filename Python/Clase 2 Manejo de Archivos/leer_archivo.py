
archivo = open('Prueba.txt', 'r', encoding='utf8') # Las letras son: 'r' read, 'a' append, 'w' write, 'x'
#Si ela archivo txt lo tengo en otra carpeta debo especificar la direccion en Linux Mint es: /home/ariel/Documentos/Tecnicatura/Codigo-Critico-Tercer-Semestre/Python/Clase 2 Manejo de Archivos/Prueba.txt
#print(archivo.read())
#print(archivo.read(16))
#print(archivo.read(10)) # Continuamos desde la linea anterior
print(archivo.readline())
print(archivo.readline())


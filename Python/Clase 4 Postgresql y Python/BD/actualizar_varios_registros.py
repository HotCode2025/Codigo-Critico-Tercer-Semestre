import psycopg2 # Esto es para poder conectarnos a Postgre

conexion = psycopg2.connect(
    user= 'ariel',
    password='admin',
    host='127.0.0.1',
    port='5432',
    database='test_bd'
)

# CODIGO MEJORADO SE HACE ASI
try:
    with conexion:
        with conexion.cursor() as cursor:
            sentencia = 'UPDATE persona SET nombre=%s, apellido=%s, email=%s WHERE id_persona=%s' #SET que columna modificio y where como filtro de lo que se va a modificar
            valores = (
                ('Juan', 'Perez', 'jperez|@gmail.com', 4),
                ('Romina', 'Ayala', 'rayala@gmail.com', 5)
            ) #Esto es una tupla de tuplas
            cursor.executemany(sentencia, valores) #se le agrega many cuando son varios registros a actualizar executemany sino no va
            registros_actualizados = cursor.rowcount
            print(f'Los registros  actualizados son: {registros_actualizados}')


except Exception as e:
    print(f'Ocurrio un error: {e}')
finally:
    conexion.close()  #DEBO CERRAR LA CONEXION CON EL FINALLY
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
            sentencia = 'DELETE FROM persona WHERE id_persona=%s' #Sino coloco el filtro del WHERE puedo borrar toda la tabla.
            entrada = input('Digite el numero de registro a elminar: ')
            valores = (entrada,) #Es una TUPLA de valores si o si va con la coma
            cursor.execute(sentencia, valores)
            registros_eliminados = cursor.rowcount
            print(f'Los registros  eliminados son: {registros_eliminados}')


except Exception as e:
    print(f'Ocurrio un error: {e}')
finally:
    conexion.close()  #DEBO CERRAR LA CONEXION CON EL FINALLY
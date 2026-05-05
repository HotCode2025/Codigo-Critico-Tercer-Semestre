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
            sentencia ='SELECT * FROM persona'
            cursor.execute(sentencia) #De esta manera ejecutamos la sentencia
            registros = cursor.fetchall() # Recuperamos todos los registros que serán una lista
            print(registros)
except Exception as e:
    print(f'Ocurrio un error: {e}')
finally:
    conexion.close()  #DEBO CERRAR LA CONEXION CON EL FINALLY

#https://www.psycopg.org/docs/usage.html
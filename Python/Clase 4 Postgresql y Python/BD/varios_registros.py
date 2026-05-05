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
            sentencia = 'SELECT * FROM persona WHERE id_persona IN %s'  # %s PLACEHOLDER Usar solo un registro filtro
            entrada = input('Digite los id_persona a buscar (separados por como): ')
            llaves_primarias = (tuple(entrada.split(', ')),)
            cursor.execute(sentencia, llaves_primarias) #De esta manera ejecutamos la sentencia
            registros = cursor.fetchall() # Recuperamos todos los registros que serán una lista
            for registro in registros:
                print(registro)

except Exception as e:
    print(f'Ocurrio un error: {e}')
finally:
    conexion.close()  #DEBO CERRAR LA CONEXION CON EL FINALLY


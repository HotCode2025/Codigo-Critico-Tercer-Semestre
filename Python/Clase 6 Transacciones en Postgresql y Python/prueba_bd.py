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
            # sentencia ='SELECT * FROM persona' # Quito asterisco ya que eso signidica todo
            sentencia = 'SELECT * FROM persona WHERE id_persona = %s'  # %s PLACEHOLDER Usar solo un registro filtro
            # sentencia = 'SELECT id_persona, nombre From Persona' solo seleccino ahi id y persona

            id_persona = input('Digite un número para el id_persona: ') #defino el parametro y el placeholder busca valor
            cursor.execute(sentencia, (id_persona,)) #se hace en tuplas la eleccion de valores. La tupla lleva siempre coma ,
            # cursor.execute(sentencia) #De esta manera ejecutamos la sentencia
            #registros = cursor.fetchall() # Recuperamos todos los registros que serán una lista
            registros = cursor.fetchone() #nos muestra directamente la tupla y desaparece la lista
            print(registros)
except Exception as e:
    print(f'Ocurrio un error: {e}')
finally:
    conexion.close()  #DEBO CERRAR LA CONEXION CON EL FINALLY

#https://www.psycopg.org/docs/usage.html
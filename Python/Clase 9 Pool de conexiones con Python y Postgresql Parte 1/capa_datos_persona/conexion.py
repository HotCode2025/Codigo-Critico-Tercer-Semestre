from psycopg2 import pool ##renombro como bd
## psycopg2 as bd Otra manera de importar el psycopg2

from logger_base import log

import psycopg2 as bd
#psycopg2 as db otra manera de importar el psycopg2
from logger_base import log
import sys

class Conexion:
    _DATABASE = 'test_bd'
    _USERNAME = 'ariel'
    _PASSWORD = 'admin'
    _DEB_PORT = '5432'
    _HOST = '127.0.0.1'
    _MIN_CON = 1
    _MAX_CON = 5
    _pool = None

    @classmethod  ##METODO OBTENER CONEXION.
    def obtenerConexion(cls):
        pass

    @classmethod
    def obtenerCursor(cls):
        pass

    @classmethod
    def obtenerPool(cls):
        if cls._pool is None:
            try:
                cls._pool = pool.SimpleConnectionPool()



if __name__ == '__main__':
    pass

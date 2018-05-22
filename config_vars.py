'''configuration values for api'''
from argon2 import PasswordHasher
from peewee import PostgresqlDatabase, SqliteDatabase
import os

DEBUG = True
HOST = '0.0.0.0'
PORT = 8000
SECRET_KEY = 'SD:FLKDWUdsfk;aifaw:WEFJuqhw*GF%DR$*&%$eFgYrtUjhuu9IuyR5p^TGIYv'
DEFAULT_RATE = '100/hour'
HASHER = PasswordHasher()
try:
    DATABASE = PostgresqlDatabase(
        os.environ['database'],
        host=os.environ['host'],
        port=os.environ['port'],
        user=os.environ['user'],
        password=os.environ['password'],
        sslmode=os.environ['sslmode'],
        sslrootcert=os.environ['sslrootcert']
    )
except KeyError:
    DATABASE = SqliteDatabase('courses.sqlite')

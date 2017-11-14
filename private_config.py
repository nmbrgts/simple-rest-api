'''configuration values for api'''
from argon2 import PasswordHasher
from peewee import PostgresqlDatabase

DEBUG = True
HOST = '0.0.0.0'
PORT = 8000
SECRET_KEY = 'SD:FLKDWUdsfk;aifaw:WEFJuqhw*GF%DR$*&%$eFgYrtUjhuu9IuyR5p^TGIYv'
DEFAULT_RATE = '100/hour'
HASHER = PasswordHasher()
DATABASE = PostgresqlDatabase(
    'restdb3',
    host='restdb3.cewxu2uwvb5v.us-west-2.rds.amazonaws.com',
    port='5432',
    user='nmbrgts',
    password='mypassword'
)

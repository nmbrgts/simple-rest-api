'''configuration values for api'''
from argon2 import PasswordHasher
from peewee import PostgresqlDatabase
import os

DEBUG = True
HOST = '0.0.0.0'
PORT = 8000
SECRET_KEY = 'SD:FLKDWUdsfk;aifaw:WEFJuqhw*GF%DR$*&%$eFgYrtUjhuu9IuyR5p^TGIYv'
DEFAULT_RATE = '100/hour'
HASHER = PasswordHasher()
DATABASE = PostgresqlDatabase(
    os.environ['database'],
    host=os.environ['host'],
    port=os.environ['port'],
    user=os.environ['user'],
    password=os.environ['password'],
    sslmode=os.environ['sslmode'],
    sslrootcert=os.environ['sslrootcert']
)
# DATABASE = PostgresqlDatabase(
#     'course_db',
#     host='course-api.chamxx5zi4uv.us-west-2.rds.amazonaws.com',
#     port='5432',
#     user='tnick',
#     password='password1',
#     sslmode='verify-ca',
#     sslrootcert='./config/amazon-rds-ca-cert.pem'
# )

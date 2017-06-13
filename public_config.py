'''configuration values for api'''
from argon2 import PasswordHasher
from peewee import SqliteDatabase

DEBUG = True
HOST = '0.0.0.0'
PORT = 8000
SECRET_KEY = 'PeOdifpaea9348T7jgt7jgfeFhYfRYu*&%$eFgYrtUjhuu9IuyR5p'
DEFAULT_RATE = '100/hour'
DATABASE = SqliteDatabase('courses.sqlite')
HASHER = PasswordHasher()

import datetime
import json
from argon2 import PasswordHasher
from itsdangerous import (
    TimedJSONWebSignatureSerializer as Serializer,
    BadSignature, SignatureExpired
)
from peewee import *

import config

DATABASE = SqliteDatabase('courses.sqlite')
# DATABASE = PostgresqlDatabase(
#     'restDB',
#     host='flask-rest-db.cewxu2uwvb5v.us-west-2.rds.amazonaws.com',
#     port='5432',
#     user='nmbrgts',
#     password='mypassword'
# )
HASHER = PasswordHasher()


class User(Model):
    username = CharField(unique=True)
    email = CharField(unique=True)
    password = CharField()

    class Meta:
        database = DATABASE

    @classmethod
    def create_user(cls, username, email, password, **kwargs):
        email = email.lower()
        try:
            cls.select().where(
                (cls.email == email) | (cls.username ** username)
            ).get()
        except cls.DoesNotExist:
            user = cls(username=username, email=email)
            user.password = user.set_password(password)
            user.save()
            return user
        else:
            raise Exception('User with that email or username already exists')

    @classmethod
    def update_user(cls, id, username, email, password, **kwargs):
        email = email.lower()
        try:
            user = cls.select().where(cls.id == id).get()
        except cls.DoesNotExist:
            raise Exception('User id does not exist')
        else:
            user.username = username
            user.email = email
            user.password = user.set_password(password)
            user.save()
            user.password = password  # for return of password to user
            return user

    @staticmethod
    def verify_auth_token(token):
        serializer = Serializer(config.SECRET_KEY)
        try:
            data = serializer.loads(token)
        except (SignatureExpired, BadSignature):
            return None
        else:
            user = User.get(User.id == data['id'])
            return user

    @staticmethod
    def set_password(password):
        return HASHER.hash(password)

    def verify_password(self, password):
        return HASHER.verify(self.password, password)

    def generate_auth_token(self, expires=3600):
        serializer = Serializer(config.SECRET_KEY, expires_in=expires)
        return serializer.dumps({'id': self.id})


class Course(Model):
    title = CharField()
    url = CharField(unique=True)
    created_at = DateTimeField(default=datetime.datetime.now)

    class Meta:
        database = DATABASE


class Review(Model):
    course = ForeignKeyField(Course, related_name='review_set')
    created_by = ForeignKeyField(User, related_name='review_set')
    rating = IntegerField()
    comment = TextField(default='')
    created_at = DateTimeField(default=datetime.datetime.now)

    class Meta:
        database = DATABASE


class Edit(Model):
    review = ForeignKeyField(Review, related_name='edit_set',
                             null=True, default=None)
    course = ForeignKeyField(Course, related_name='edit_set',
                             null=True, default=None)
    created_by = ForeignKeyField(User, related_name='edit_set')
    entry = TextField()
    status = CharField(
        default='pending',
        constraints=[
            Check("status IN ('pending', 'approved', 'denied')")
        ])
    created_at = DateTimeField(default=datetime.datetime.now)

    @classmethod
    def update_edit(cls, edit_id, user, **edit_args):
        """Verifies that the user trying to update an edit is the edit's
        creator, the applies the update.
        Input: Update Args
        Output: An instance of the Edit Model for the updated entry
        Raises: 'Edit does not exist' if the entry doesn't exist"""
        try:
            (cls.update(**edit_args)
                .where(cls.id == edit_id,
                       cls.created_by == user)
                .execute())
        except cls.DoesNotExist:
            raise('Edit does not exist')
        else:
            return cls.get(cls.id == edit_id)

    class Meta:
        database = DATABASE


class Comment(Model):
    review = ForeignKeyField(Review, related_name='comment_set',
                             null=True, default=None)
    created_by = ForeignKeyField(User, related_name='comment_set')
    created_at = DateTimeField(default=datetime.datetime.now)
    parent_comment = ForeignKeyField('self', related_name='child_comments',
                                     null=True, default=None)
    comment = TextField(default='')

    @classmethod
    def get_children(cls, id):
        """returns a set of child comments for a given comment id
        INPUT: parent_id the id number of a comment
        RETURNS: peewee query object containing the children of the comment"""
        try:
            Parent = cls.alias()
            children = (cls.select()
                           .join(Parent, on=(cls.parent_comment == Parent.id))
                           .where(Parent.id == id)
                           .execute())
        except (cls.DoesNotExist, Parent.DoesNotExist):
            # doesn't seem to raise... will simply return empty...
            # I think this is desireable though
            raise('Comment does not exist')
        else:
            return children

    class Meta:
        database = DATABASE


def initialize():
    DATABASE.connect()
    DATABASE.create_tables([User, Course, Review, Edit, Comment], safe=True)
    DATABASE.close()

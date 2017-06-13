import datetime
import json
from itsdangerous import (
    TimedJSONWebSignatureSerializer as Serializer,
    BadSignature, SignatureExpired
)
from peewee import *

try:
    import private_config as config
except ImportError:
    import public_config as config


class User(Model):
    username = CharField(unique=True)
    email = CharField(unique=True)
    password = CharField()
    karma = IntegerField(default=0)

    class Meta:
        database = config.DATABASE

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
        return config.HASHER.hash(password)

    def verify_password(self, password):
        return config.HASHER.verify(self.password, password)

    def generate_auth_token(self, expires=3600):
        serializer = Serializer(config.SECRET_KEY, expires_in=expires)
        return serializer.dumps({'id': self.id})


class Course(Model):
    title = CharField()
    url = CharField(unique=True)
    created_at = DateTimeField(default=datetime.datetime.now)

    class Meta:
        database = config.DATABASE


class Review(Model):
    course = ForeignKeyField(Course, related_name='review_set')
    created_by = ForeignKeyField(User, related_name='review_set')
    rating = IntegerField()
    comment = TextField(default='')
    created_at = DateTimeField(default=datetime.datetime.now)
    upvotes = IntegerField(default=0)
    downvotes = IntegerField(default=0)

    class Meta:
        database = config.DATABASE


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
        database = config.DATABASE


class Comment(Model):
    review = ForeignKeyField(Review, related_name='comment_set',
                             null=True, default=None)
    created_by = ForeignKeyField(User, related_name='comment_set')
    created_at = DateTimeField(default=datetime.datetime.now)
    parent_comment = ForeignKeyField('self', related_name='child_comments',
                                     null=True, default=None)
    comment = TextField(default='')
    upvotes = IntegerField(default=0)
    downvotes = IntegerField(default=0)

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
        database = config.DATABASE


class Tag(Model):
    tag = CharField(unique=True)
    alternatives = TextField()

    class Meta:
        database = config.DATABASE


class TagLink(Model):
    tag = ForeignKeyField(Tag, related_name='link_set')
    course = ForeignKeyField(Course, related_name='link_set')

    class Meta:
        database = config.DATABASE
        contraints = [SQL('UNIQUE(tag, course)')]


class Vote(Model):
    user = ForeignKeyField(User, related_name='vote_set')
    upvote = IntegerField(default=0,
                          constraints=[
                              Check('upvote = 1 OR upvote = 0')
                          ])
    downvote = IntegerField(default=0,
                            constraints=[
                                Check('downvote = 1 OR downvote = 0')
                            ])
    review = ForeignKeyField(Review, related_name='vote_set',
                             null=True, default=None)
    comment = ForeignKeyField(Comment, related_name='vote_set',
                              null=True, default=None)
    @staticmethod
    def verify_vote(review=None, comment=None,
                    upvote=None, downvote=None):
        if (review and comment) or (upvote and downvote):
            raise Exception('You may only upvote or downvote one entry at a time!')
        if upvote:
            upvote = 1
            downvote = 0
        else:
            upvote = 0
            downvote = 1
        return upvote, downvote


    @classmethod
    def cast_vote(cls, user, comment=None,
                  review=None, upvote=None, downvote=None):
        upvote, downvote = cls.verify_vote(comment, review,
                                           upvote, downvote)
        try:
            vote = cls.get(cls.user == user,
                           cls.review == review,
                           cls.comment == comment)
        except cls.DoesNotExist:
            vote = cls.create(user=user,
                              review=review,
                              comment=comment,
                              upvote=upvote,
                              downvote=downvote)
            return vote
        else:
            vote.upvote = upvote
            vote.downvote = downvote
            vote.save()
            return vote

    @classmethod
    def uncast_vote(cls, user, comment=None, review=None):
        upvote, downvote = cls.verify_vote(comment, review, 1, None)
        try:
            (cls.delete().where(cls.user == user,
                                cls.review == review,
                                cls.comment == comment)
                         .execute())
        except cls.DoesNotExist:
            raise Exception('Nothing to delete!')

    class Meta:
        database = config.DATABASE
        contraints = [SQL('UNIQUE(user, review, comment)')]


def initialize():
    config.DATABASE.connect()
    config.DATABASE.create_tables([User, Course,
                            Review, Edit,
                            Comment, Tag,
                            TagLink, Vote],
                           safe=True)
    config.DATABASE.close()

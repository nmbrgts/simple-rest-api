import json
from flask import Blueprint, url_for, make_response
from flask_restful import (
    Resource, Api, inputs, reqparse, fields, marshal, marshal_with
)

import models


# should contain user information that will be used internally
internal_user_fields = {
    'id': fields.Integer,
    'username': fields.String,
    'email': fields.String,
    'password': fields.String,
    'reviews_written': fields.List(fields.String)
}
# should contain user information that can be exposed through api
external_user_fields = {
    'id': fields.Integer,
    'username': fields.String,
    'reviews_written': fields.List(fields.String)
}


def add_reviews(user):
    # should add a list of user reviews
    # to a user model
    user.reviews_written = [url_for('resources.reviews.review', id=review.id)
                            for review in user.review_set]
    return user


class UserList(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument(
            'username',
            type=str,
            required=True,
            help='Username not provided',
            location=['form', 'json']
        )
        self.reqparse.add_argument(
            'email',
            type=str,
            required=True,
            help='Email not provided',
            location=['form', 'json']
        )
        self.reqparse.add_argument(
            'password',
            type=str,
            required=True,
            help='Password not providded',
            location=['form', 'json']
        )
        self.reqparse.add_argument(
            'verify_password',
            type=str,
            required=True,
            help='Verifcation password not providded',
            location=['form', 'json']
        )
        super().__init__()

    def get(self):
        # should get the list of users
        # returned users should have the following fields:
        #  username
        #  reviews
        users = [marshal(user, external_user_fields)
                 for user in models.User.select()]
        return {'users': users}

    def post(self):
        # should create a new database entry for a new user
        # if a user already exists, this process should return
        # an error message, otherwise it will return user info as
        # created?
        args = self.reqparse.parse_args()
        if args.get('password') == args.get('verify_password'):
            try:
                user = models.User.create_user(**args)
            except Exception as e:
                return make_response(json.dumps({'error': str(e)}), 400)
            else:
                return marshal(user, external_user_fields), 201
        return make_response(
                    json.dumps(
                        {'error':
                            'Password and verfication password do not match'}
                    ),
                    400)


class User(Resource):
    def __init__(self):
        self.reqparse = reparse.RequestParser()
        self.reqparse.add_argument(
            'username',
            type=str,
            required=True,
            help='Username not supplied',
            location=['form', 'json']
        )
        self.reqparse.add_argument(
            'email',
            type=str,
            required=True,
            help='Email not supplied',
            location=['form', 'json']
        )
        self.reqparse.add_argument(
            'password',
            type=str,
            required=True,
            help='Password not supplied',
            location=['form', 'json']
        )
        self.reqparse.add_argument(
            'verify_password',
            type=str,
            required=True,
            help='Password verification not supplied',
            location=['form', 'json']
        )
        # add profile options?
        # perhaps profiles should be a seperate resource?
        super().__init__()

    def get(self, id):
        user = models.User.get(models.User.id == id)
        return marshal(user, external_user_fields), 200


user_api = Blueprint('resources.users', __name__)

api = Api(user_api)
api.add_resource(
    UserList,
    '/users',
    endpoint='users'
)
api.add_resource(
    User,
    '/users/<int:id>',
    endpoint='user'
)

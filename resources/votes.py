from flask import (
    jsonify, Blueprint, url_for,
    abort, g, make_response
)

from flask_restful import (
    Resource, Api, reqparse, inputs,
    fields, marshal, marshal_with
)

import re
import json

import models

from auth import auth


class UpVote(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument(
            'url', #url for upvote target
            type=str,
            help='url must be a url target for vote in the form of a string',
            required=True,
            location=['form', 'json']
        )

    @auth.login_required
    def post(self):
        args = self.reqparse.parse_args()
        return vote(args, 'upvote')


class DownVote(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument(
            'url',  # url for downvote target
            type=str,
            help='url must be a url target for vote in the form of a string',
            required=True,
            location=['form', 'json']
        )

    @auth.login_required
    def post(self):
        args = self.reqparse.parse_args()
        return vote(args, 'downvote')


def vote(args, vote_field):
    target = {}
    regex = r'^.*/(\w+)s/(\d+)$'
    try:
        (field, id) = re.findall(regex, args['url'])[0]
    except IndexError:
        return make_response(
            json.dumps({'message': 'invalid url/uri'}),
            403,
        )
    else:
        try:
            if field == 'review':
                value = models.Review.get(
                    models.Review.id == id
                )
            elif field == 'comment':
                value = models.Comment.get(
                    models.Comment.id == id
                )
            else:
                return make_response(
                    json.dumps({'message': 'invalid url/uri'}),
                    403,
                )
            target[field] = value
            target[vote_field] = 1
            models.Vote.cast_vote(
                user=g.user,
                **target
            )
        except (models.Review.DoesNotExist,
                models.Comment.DoesNotExist):
            return make_response(
                json.dumps({'message': 'invalid comment/review'}),
                500,
            )
        else:
            return make_response(
                '',
                200,
                {'location': url_for('resources' +
                                        '.' + field +
                                        's.' + field,
                                        id=id)}
            )


votes_api = Blueprint('resources.votes', __name__)
api = Api(votes_api)
api.add_resource(
    UpVote,
    '/upvote',
    endpoint='upvote'
)
api.add_resource(
    DownVote,
    '/downvote',
    endpoint='downvote'
)

import json
from flask import Blueprint, g, make_response, url_for
from flask_restful import (
    Api, fields, inputs, marshal, reqparse, Resource
)

import models
from auth import auth

edit_fields = {
    'id': fields.Integer,
    'edit_for': fields.String,
    'entry': fields.Raw,
    'status': fields.String,
    'created_at': fields.DateTime(dt_format='iso8601'),
    'created_by': fields.String(attribute='created_by_url')
}


def verify_edit(edit_args):
    """edit must contain one foriegn key, but not both. keys cannot be 0.
    input: edit_args
    output: Bool, false fails validation
    """
    return bool(edit_args['course']) != bool(edit_args['class'])


def add_for(edit):
    try:
        edit.edit_for = url_for('resources.courses.course', id=edit.course.id)
    except AttributeError:
        try:
            edit.edit_for = url_for('resources.reviews.review', id=edit.review.id)
        except AttributeError:
            raise Exception('No valid course or reivew id provided')
        else:
            return edit
    else:
        return edit


def add_user(edit):
    # convert user id to endpoint url for consumption
    edit.created_by_url = url_for('resources.users.user',
                                  id=edit.created_by.id)
    return edit


def load_entry(edit):
    edit.entry = json.loads(edit.entry)
    return edit


class EditList(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument(
            'course',
            type=int,
            required=False,
            help='Course id must be integer or None',
            default=None,
            location=['form', 'json']
        )
        self.reqparse.add_argument(
            'review',
            type=int,
            required=False,
            help='Review id must be integer or None',
            default=None,
            location=['form', 'json']
        )
        self.reqparse.add_argument(
            'entry',
            type=str,
            help='No edited entry provided.',
            required=True,
            location=['form', 'json']
        )
        super().__init__()

    def get(self):
        edits = models.Edit.select()
        edits = [marshal(load_entry(add_user(add_for(edit))), edit_fields)
                 for edit in edits]
        return {'edits': edits}

    @auth.login_required
    def post(self):
        args = self.reqparse.parse_args()
        args['created_by'] = g.user.id
        edit = models.Edit.create(**args)
        return marshal(load_entry(add_user(add_for(edit))), edit_fields)


class Edits(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument(
            'course',
            type=int,
            required=False,
            default=None,
            location=['form', 'json'],
            help=''
        )
        self.reqparse.add_argument(
            'review',
            type=int,
            required=False,
            default=None,
            location=['form', 'json'],
            help=''
        )
        self.reqparse.add_argument(
            'entry',
            type=str,
            required=True,
            location=['form', 'json'],
            help=''
        )
        super().__init__()

    def get(self, id):
        edit = models.Edit.get(models.Edit.id == id)
        return marshal(load_entry(add_user(add_for(edit))), edit_fields)

    @auth.login_required
    def put(self, id):
        # call a verify method from models
        args = self.reqparse.parse_args()
        args['status'] = 'pending'
        try:
            edit = models.Edit.update_edit(id, g.user, **args)
        except Exception as e:
            return {'Error': str(e)}
        else:
            return marshal(load_entry(add_user(add_for(edit))), edit_fields)

    @auth.login_required
    def delete(self, id):
        # call a verify method from models
        try:
            edit = (models.Edit.select()
                          .where(models.Edit.id == id,
                                 models.Edit.created_by == g.user)
                          .ececute())
        except models.Edit.DoesNotExist:
            return make_response(json.dumps(
                {'Error': 'Edit does not exist or does not belong to user'}
                ), 403)
        else:
            edit.delete_instance()
            return '', 204, {'location': url_for('resources.edits.edits')}

edits_api = Blueprint('resources.edits', __name__)

api = Api(edits_api)
api.add_resource(
    EditList,
    '/edits',
    endpoint='edits'
)
api.add_resource(
    Edits,
    '/edits/<int:id>',
    endpoint='edit'
)

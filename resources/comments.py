import json
from flask import Blueprint, g, make_response, url_for
from flask_restful import (
    marshal, inputs, fields, reqparse, Resource, Api, abort
)

import models
from auth import auth

COMMENT_FIELDS = {
    'by': fields.String,
    'date': fields.DateTime(attribute='created_at'),
    'review': fields.String(attribute='review_url'),
    'parent_comment': fields.String(attribute='p_comment_url'),
    'comment': fields.String,
    'children': fields.List(fields.String),
}


def validate_parents(**request_args):
    """A comment should only have one valid parent.
    Either a parent_comment or a review.

    Input: request_args, the arguments parsed from the request
    Output: None. Aborts if request has more than one parent.
    """
    parents = []
    parents.append(request_args.get('parent_comment', None))
    parents.append(request_args.get('review', None))
    valid_parent = [parent is not None for parent in parents]
    if not any(valid_parent) or all(valid_parent):
        raise Exception('Comments can only have one valid parent.')


def validate_put(request_parser, comment, request_args):
    parser_args = [arg.name for arg in request_parser.args]
    for arg in parser_args:
        comment_arg = getattr(comment, arg, None)
        request_arg = request_args.get(arg, None)
        if comment_arg != request_arg:
            raise Exception('Users may only change the "Comment" field.')


def add_children(comment):
    try:
        comment.children = [url_for('resources.comments.comment', id=child.id)
                            for child in comment.child_comments]
    except AttributeError:
        comment.children = []
    finally:
        return comment


def add_parents(comment):
    try:
        comment.p_comment_url = url_for('resources.comments.comment',
                                        id=comment.parent_comment.id)
    except AttributeError:
        comment.review_url = url_for('resources.reviews.review',
                                     id=comment.review_id)
    finally:
        return comment


def add_user(comment):
    comment.by = url_for('resources.users.user',
                         id=comment.created_by.id)
    return comment


def add_fields(comment):
    return add_user(add_parents(add_children(comment)))


class CommentList(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument(
            'review',
            type=int,
            required=False,
            default=None,
            location=['form', 'json'],
        )
        self.reqparse.add_argument(
            'parent_comment',
            type=int,
            required=False,
            default=None,
            location=['form', 'json'],
        )
        self.reqparse.add_argument(
            'comment',
            type=str,
            required=True,
            help='No empy comments please!',
            location=['form', 'json'],
        )
        super().__init__()

    def get(self):
        comments = models.Comment.select().execute()
        comments = [marshal(add_fields(comment), COMMENT_FIELDS)
                    for comment in comments]
        return {'comments': comments}

    @auth.login_required
    def post(self):
        args = self.reqparse.parse_args()
        try:
            validate_parents(**args)
        except Exception as e:
            return make_response(json.dumps(
                {'error': str(e)}
            ), 403)
        else:
            try:
                comment = models.Comment.create(**args, created_by=g.user)
            except Exception as e:
                return make_response(json.dumps(
                    {'error': str(e)}
                ), 500)
            else:
                return marshal(add_fields(comment), COMMENT_FIELDS)


class Comment(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument(
            'review',
            type=int,
            required=False,
            default=None,
            location=['form', 'json'],
        )
        self.reqparse.add_argument(
            'parent_comment',
            type=int,
            required=False,
            default=None,
            location=['form', 'json'],
        )
        self.reqparse.add_argument(
            'comment',
            type=str,
            required=True,
            help='No empty comments please!',
            location=['form', 'json'],
        )
        super().__init__()

    def get(self, id):
        try:
            comment = models.Comment.get(models.Comment.id == id)
        except models.Comment.DoesNotExist:
            return make_response(json.dumps(
                {'error': 'invalid comment id'}
            ), 403)
        else:
            return marshal(add_fields(comment), COMMENT_FIELDS)

    @auth.login_required
    def put(self, id):
        args = self.reqparse.parse_args()
        try:
            comment = models.Comment.get(models.Comment.id == id,
                                         models.Comment.created_by == g.user)
        except models.Comment.DoesNotExist:
            return make_response(json.dumps(
                {'error': 'invalid comment id'}
            ), 403)
        else:
            try:
                validate_put(self.reqparse, comment, args)
            except Exception as e:
                return make_response(json.dumps(
                    {'error': str(e)}
                ), 403)
            else:
                comment.comment = args['comment']
                return (marshal(add_fields(comment), COMMENT_FIELDS), 200,
                        {'location': url_for('resources.review.review', id=id)})

    def delete(self, id):
        try:
            (models.Comment.delete()
                   .where(models.Comment.id == id,
                          models.Comment.created_by == g.user))
        except models.Comment.DoesNotExist:
            return make_response(json.dumps(
                {'error': 'comment does not exist'}
            ), 403)
        else:
            return '', 204, {'location': url_for('resources.comments.comments')}


comments_api = Blueprint('resources.comments', __name__)

api = Api(comments_api)
api.add_resource(
    CommentList,
    '/comments',
    endpoint='comments'
)
api.add_resource(
    Comment,
    '/comments/<int:id>',
    endpoint='comment'
)

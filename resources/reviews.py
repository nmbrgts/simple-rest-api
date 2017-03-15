from flask import Blueprint, url_for, abort, make_response, g

from flask_restful import (
    Resource, Api, reqparse, inputs,
    fields, marshal, marshal_with
)

import json

import models

from auth import auth

review_fields = {
    'id': fields.Integer,
    'for_course': fields.String,
    'rating': fields.Integer,
    'comment': fields.String(default=''),
    'by_user': fields.String,
    'created_at': fields.DateTime
}


def review_or_404(review_id):
    try:
        review = models.Review.get(models.Review.id == review_id)
    except models.Review.DoesNotExist:
        abort(404)
    else:
        return review


def add_course(review):
    review.for_course = url_for('resources.courses.course',
                                id=review.course.id)
    return review


def add_user(review):
    review.by_user = url_for('resources.users.user',
                             id=review.created_by.id)
    return review


class ReviewList(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument(
            'course',
            required=True,
            help='No course provided :C',
            type=inputs.positive,
            location=['form', 'json'],
        )
        self.reqparse.add_argument(
            'rating',
            required=True,
            help='No rating provided :C',
            location=['form', 'json'],
            type=inputs.int_range(1, 5)
        )
        self.reqparse.add_argument(
            'comment',
            required=False,
            nullable=True,
            location=['form', 'json'],
            default=''
        )
        super().__init__()

    def get(self):
        query = models.Review.select()
        reviews = [marshal(add_user(add_course(review)), review_fields)
                   for review in query]
        return {'reviews': reviews}

    @marshal_with(review_fields)
    @auth.login_required
    def post(self):
        args = self.reqparse.parse_args()
        review = models.Review.create(
            created_by=g.user,
            **args
        )
        return (add_user(add_course(review)), 201,
                {'location':
                 url_for('resources.reviews.review', id=review.id)})


class Review(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument(
            'course',
            required=True,
            help='Course not provided',
            type=inputs.positive,
            location=['form', 'json']
        )
        self.reqparse.add_argument(
            'rating',
            required=True,
            help='No rating provived',
            type=inputs.int_range(1, 5),
            location=['form', 'json']
        )
        self.reqparse.add_argument(
            'comment',
            required=False,
            nullable=True,
            default='',
            location=['form', 'json']
        )
        super().__init__()

    @marshal_with(review_fields)
    def get(self, id):
        return add_user(add_course(review_or_404(id)))

    @marshal_with(review_fields)
    @auth.login_required
    def put(self, id):
        args = self.reqparse.parse_args()
        try:
            review = models.Review.select().where(
                models.Review.id == id,
                models.Review.created_by == g.user
            ).get()
        except models.Review.DoesNotExist:
            return make_response(json.dumps(
                {'error': 'That review does not exist or is not editable'}
            ), 403)
        else:
            review.update(**args)
            return (add_user(add_course(review)), 200,
                    {'location': url_for('resources.reviews.review', id=id)})

    @auth.login_required
    def delete(self, id):
        try:
            review = models.Review.select().where(
                models.Review.created_by == g.user,
                models.Review.id == id
            ).get()
        except models.Review.DoesNotExist:
            return make_response(json.dumps(
                {'error': 'That review does not exist or is not editable'}
            ), 403)
        else:
            review.delete_instance()
            return '', 204, {'location': url_for('resources.reviews.reviews')}


reviews_api = Blueprint('resources.reviews', __name__)
api = Api(reviews_api)
api.add_resource(
    ReviewList,
    '/reviews',
    endpoint='reviews'
)
api.add_resource(
    Review,
    '/reviews/<int:id>',
    endpoint='review'
)

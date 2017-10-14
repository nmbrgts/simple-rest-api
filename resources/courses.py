from flask import jsonify, Blueprint, url_for, abort, make_response

from flask_restful import (
    Resource, Api, reqparse, inputs,
    fields, marshal, marshal_with
)

import models
import json

from auth import auth

course_fields = {
    'id': fields.Integer,
    'title': fields.String,
    'url': fields.String,
    'reviews': fields.List(fields.String),
    'tags': fields.List(fields.String),
}


def add_reviews(course):
    course.reviews = [url_for('resources.reviews.review', id=review.id)
                      for review in course.review_set]
    return course


def add_tags(course):
    course.tags = [link.tag.tag for link in course.link_set]
    return course


def course_or_404(course_id):
    try:
        course = models.Course.get(models.Course.id == course_id)
    except models.Course.DoesNotExist:
        abort(404)
    else:
        return course


class CourseList(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument(
            'title',
            required=True,
            help='No course title provided :C',
            location=['form', 'json'],
        )
        self.reqparse.add_argument(
            'url',
            required=True,
            help='No course URL provided :C',
            location=['form', 'json'],
            type=inputs.url,
        )
        super().__init__()

    def get(self):
        courses = [marshal(add_tags(add_reviews(course)), course_fields)
                   for course in models.Course.select()]
        return {'courses': courses}

    # i don't like the way this function looks but, couldn't find a cleaner
    # way to ensure that this function returns an error if the course already
    # exists... maybe this functionality should be in the orm module?
    @auth.login_required
    def post(self):
        args = self.reqparse.parse_args()
        try:
            course = models.Course.get(models.Course.title == args['title'],
                                       models.Course.url == args['url'])
            return make_response(json.dumps({
                       'message' : 'entry already exists'
                   }), 403, {
                       'location': url_for('resources.courses.course',
                                           id=course.id)
                   })
        except models.Course.DoesNotExist:
            course = models.Course.create(**args)
            return (marshal(add_tags(add_reviews(course)),
                            course_fields),
                    201,
                    {'location': url_for('resources.courses.course',
                                          id=course.id)})


class Course(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument(
            'title',
            required=True,
            help='No title provided',
            location=['form', 'json']
        )
        self.reqparse.add_argument(
            'url',
            required=True,
            help='No course URL provided',
            type=inputs.url,
            location=['form', 'json']
        )
        super().__init__()

    # marshals output, works best with single return
    @marshal_with(course_fields)
    def get(self, id):
        return add_tags(add_reviews(course_or_404(id)))

    @auth.login_required
    @marshal_with(course_fields)
    def put(self, id):
        args = self.reqparse.parse_args()
        query = models.Course.update(**args).where(models.Course.id == id)
        query.execute()
        return (add_tags(add_reviews(course_or_404(id))), 200,
                {'location': url_for('resources.courses.course', id=id)})

    @auth.login_required
    def delete(self, id):
        query = models.Course.delete().where(models.Course.id == id)
        query.execute()
        return '', 204, {'location': url_for('resources.courses.courses')}


courses_api = Blueprint('resources.courses', __name__)

api = Api(courses_api)
api.add_resource(
    CourseList,
    '/api/v1/courses',
    endpoint='courses'
)
api.add_resource(
    Course,
    '/api/v1/courses/<int:id>',
    endpoint='course'
)

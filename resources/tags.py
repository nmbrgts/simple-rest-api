from flask import jsonify, Blueprint, url_for, abort, make_response
from flask_restful import (
    Resource, Api, reqparse, inputs,
    fields, marshal, marshal_with
)
import re
import json
import models
from auth import auth


class TagList(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument(
            'tag',
            required=True,
            help='No tag provided :C',
            location=['form', 'json'],
        )
        super().__init__()

    def get(self):
        tags = models.Tag.select().execute()
        return {'tags': [tag.tag for tag in tags]}

    def post(self):
        args = self.reqparse.parse_args()
        tag = models.Tag.add_tag(args['tag'])
        return {'tag': tag.tag}, 200


class Tag(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument(
            'tag',
            required=True,
            help='No tag provided :C',
            location=['form', 'json'],
        )
        self.reqparse.add_argument(
            'course',
            required=True,
            help='No tag provided :C',
            location=['form', 'json'],
        )
        super().__init__()

    @auth.login_required
    def post(self):
        regex = r'^.*/(\w+)s/(\d+)$'
        args = self.reqparse.parse_args()
        _, id = re.findall(regex, args['course'])[0]
        id = int(id)
        course = models.TagLink.tag_course(
            tag_text=args['tag'],
            course_id=id,
        )
        return ('', 200, {
                    'location':
                        url_for('resources.courses.course',
                                id=course.id)
                })


tags_api = Blueprint('resources.tags', __name__)

api = Api(tags_api)
api.add_resource(
    TagList,
    '/tags',
    endpoint='tags'
)
api.add_resource(
    Tag,
    '/addtag',
    endpoint='addtag'
)

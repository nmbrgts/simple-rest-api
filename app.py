import config
import models
from auth import auth
from resources.courses import courses_api
from resources.reviews import reviews_api
from resources.users import user_api
from resources.edits import edits_api
from resources.comments import comments_api

from flask import Flask, g, jsonify
from flask_limiter import Limiter
from flask_limiter.util import get_ipaddr

app = Flask(__name__)
app.register_blueprint(courses_api)  # add url prefix here
app.register_blueprint(reviews_api, url_prefix='/api/v1')
app.register_blueprint(user_api, url_prefix='/api/v1')
app.register_blueprint(edits_api, url_prefix='/api/v1')
app.register_blueprint(comments_api, url_prefix='/api/v1')

# simple ip address limit. other options are the user token or user name.
limiter = Limiter(app,
                  global_limits=[config.DEFAULT_RATE],
                  key_func=get_ipaddr)
# specifiy a limit for a specific blueprint
limiter.limit('40/day')(user_api)
method_limiter = limiter.limit(config.DEFAULT_RATE, per_method=True,
                               methods=['post', 'put', 'delete'])
method_limiter(courses_api)
method_limiter(reviews_api)
# # exempt a blueprint from limits
# limiter.exempt(courses_api)
# limiter.exempt(reviews_api)


@app.route('/api/v1/users/token', methods=['GET'])
@auth.login_required
def get_auth_token():
    token = g.user.generate_auth_token()
    return jsonify({'token': token.decode('ascii')})


if __name__ == '__main__':
    models.initialize()
    app.run(host=config.HOST, port=config.PORT, debug=config.DEBUG)

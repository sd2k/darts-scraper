import flask


interface = flask.Blueprint('interface', __name__)


@interface.route('/')
def index():
    return '<a href="/admin/">Click me to get to Admin!</a>'

from flask_compress import Compress
from flask_navigation import Navigation
from flask_sqlalchemy_session import flask_scoped_session

from darts import db
from darts.interface.admin import admin


compress = Compress()

nav = Navigation()

session = flask_scoped_session(db.session_factory)


def register_extensions(app):

    admin.init_app(app)

    compress.init_app(app)

    nav.init_app(app)

    session.init_app(app)

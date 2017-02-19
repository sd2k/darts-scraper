import logging
import os

from flask import Flask

from darts import settings
from darts.interface import extensions, views


def create_app():

    app = Flask(__name__)
    app.config.from_object(settings)

    extensions.register_extensions(app)

    app.register_blueprint(views.interface)

    return app


if __name__ == '__main__':
    app = create_app()

    # Reset root logger
    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)
    logging.basicConfig(level=logging.INFO)

    app.run(host='0.0.0.0', port=int(os.getenv('PORT', 5000)), debug=True)

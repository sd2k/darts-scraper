"""This module provides application instances for Gunicorn to run."""

import logging

from darts.interface.app import create_app  # noqa

# Reset root logger
for handler in logging.root.handlers[:]:
    logging.root.removeHandler(handler)
logging.basicConfig(level=logging.INFO)

app = create_app()

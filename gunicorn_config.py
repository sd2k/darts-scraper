# Gunicorn configuration file.
import os

bind = '0.0.0.0:{}'.format(os.environ.get('PORT', 5000))

workers = 4
worker_class = 'gevent'

errorlog = '-'
loglevel = 'info'
accesslog = '-'

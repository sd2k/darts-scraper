web: gunicorn -c darts/gunicorn_config.py darts.wsgi:app
web_dev: pypy darts/interface/app.py
etl: python darts/etl/main.py
worker: pypy darts/worker.py

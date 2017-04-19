FROM pypy:2

WORKDIR /app/

COPY requirements-dev.txt requirements-dev.txt
RUN pip install -r requirements-dev.txt
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY . /app/
RUN pip install .

EXPOSE 5000
CMD [ "gunicorn", "-c", "darts/gunicorn_config.py", "darts.wsgi:app" ]

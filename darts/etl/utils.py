try:
    import urlparse
except ImportError:
    import urllib.parse as urlparse


def parse_pg_url(url):
    db = urlparse.urlparse(url)
    return dict(
        host=db.hostname,
        port=db.port,
        user=db.username,
        password=db.password,
        database=db.username,
    )

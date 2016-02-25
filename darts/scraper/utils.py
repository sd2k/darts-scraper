try:
    import urlparse
except ImportError:
    import urllib.parse as urlparse

from sqlalchemy.orm.exc import NoResultFound

from darts.models import Event, Fixture, Match, Session, Tournament


session = Session()


def is_new(item_type, item_id, check_matches=False):
    if item_type == 'tournament':
        return not session.query(
            session.query(Tournament).filter(Tournament.id == item_id).exists()
        ).scalar()
    elif item_type == 'event':
        try:
            event = session.query(Event).filter(Event.id == item_id).one()
            if event.always_check and check_matches:
                return True
            elif event.always_check:
                return False
            elif check_matches:
                return not session.query(
                    session.query(
                        Match
                    ).filter(Match.event_id == item_id).exists()
                ).scalar()
        except NoResultFound:
            return True
    elif item_type == 'match':
        return not session.query(
            session.query(Match).filter(Match.id == item_id).exists()
        ).scalar()


def remove_fixture(left_player_id, right_player_id, date, logger):
    try:
        fixture = session.query(Fixture).filter(
            Fixture.date == date
        ).filter(
            (Fixture.player_1_id == left_player_id &
                Fixture.player_2_id == right_player_id) |
            (Fixture.player_1_id == right_player_id &
                Fixture.player_2_id == left_player_id)
        ).one()
        session.delete(fixture)
        session.commit()
        logger.info(
            'Removed old fixture (player 1: %s, player 2: %s, date: %s)',
            left_player_id,
            right_player_id,
            date
        )
    except NoResultFound:
        pass


def parse_pg_url(url):
    db = urlparse.urlparse(url)
    return dict(
        host=db.hostname,
        port=db.port,
        username=db.username,
        password=db.password,
        database=db.username,
    )

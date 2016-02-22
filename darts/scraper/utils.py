from sqlalchemy.orm.exc import NoResultFound

from darts.models import Event, Match, Session, Tournament


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

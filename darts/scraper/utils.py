from darts.models import Event, Session, Tournament


session = Session()


def is_new(item_type, item_id):
    if item_type == 'tournament':
        return not session.query(
            session.query(Tournament).filter(Tournament.id == item_id).exists()
        ).scalar()
    elif item_type == 'event':
        return not session.query(
            session.query(Event).filter(Event.id == item_id).exists()
        ).scalar()

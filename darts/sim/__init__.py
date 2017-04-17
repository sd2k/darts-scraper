# flake8: noqa

from darts import models

from . import oneplayer, twoplayer


class QuietDict(dict):

    def __repr__(self):
        return '<QuietDict>'

    def __str__(self):
        return '<QuietDict>'


def load_lookups(session):
    """
    Fetch the two required lookup tables from the database.

    Returns a 2-tuple containing:

    - a mapping from (score, dart ID) to shot type
    - a mapping from (score, dart ID) to a three-tuple containing
        (hit score, miss score, big miss score)
    """
    rows = session.query(models.ScoreLookup)
    score_shot_types = QuietDict()
    score_points = QuietDict()
    for row in rows:
        key = (row.score, row.dart)
        score_shot_types[key] = models.ShotTypeEnum(row.shot_type)
        score_points[key] = (
            row.hit_points,
            row.miss_points,
            row.big_miss_points,
        )

    return score_shot_types, score_points

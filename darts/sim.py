"""
Simulations of 1-player matches.
"""
import logging
import random

import enum
import numpy as np

from darts import models
from darts.models import ShotResultEnum, ShotTypeEnum


log = logging.getLogger(__name__)


DEFAULT_SHOT_TYPE = ShotTypeEnum.Treble
"Shot type to use if score doesn't appear in lookup"

DEFAULT_POINTS = (60, 20, 6)
"Points tuple to use if score doesn't appear in lookup"


def load_lookups(session):
    """
    Fetch the two required lookup tables from the database.

    Returns a 2-tuple containing:

    - a mapping from (score, dart ID) to shot type
    - a mapping from (score, dart ID) to a three-tuple containing
        (hit score, miss score, big miss score)
    """
    rows = session.query(models.ScoreLookup)
    score_shot_types = {}
    score_points = {}
    for row in rows:
        key = (row.score, row.dart)
        score_shot_types[key] = ShotTypeEnum(row.shot_type)
        score_points[key] = (
            row.hit_points,
            row.miss_points,
            row.big_miss_points,
        )

    return score_shot_types, score_points


def get_shot_type(current_score, dart_number, score_shot_types):
    """
    Get the ideal shot for a given score and dart ID.

    :param int current_score:
    :param int dart_number: the dart ID (1, 2, or 3)
    :param dict score_shot_types: mapping from (score, dart_number) to
        shot types, as returned by `~load_lookups`
    """
    return score_shot_types.get(
        (current_score, dart_number),
        DEFAULT_SHOT_TYPE,
    )


def get_result(shot_type, profile):
    """
    Return a random result for a shot type, with the probability
    determined by the given profile.

    For example, if the shot type is 'treble', the result will
    be either 0, 1 or 2 depending on the profile's 'treble' probabilities.

    :param str shot_type: type of shot, either 'treble', 'single', 'bull',
        'outer_bull', or 'double'

    :param profile: shot profile
    :type profile: :py:class:`~darts.models.Profile`

    :return: shot outcome
    :rtype: ShotResult
    """

    if shot_type == ShotTypeEnum.Single:
        return ShotResultEnum.Hit

    result = 100 * random.random()

    if shot_type == ShotTypeEnum.Treble:
        if result <= profile.treble_hit_pct:
            return ShotResultEnum.Hit
        elif result <= (100 - profile.treble_big_miss_pct):
            return ShotResultEnum.Miss
        else:
            return ShotResultEnum.BigMiss

    elif shot_type == ShotTypeEnum.Bull:
        if result <= profile.bullseye_hit_pct:
            return ShotResultEnum.Hit
        else:
            return ShotResultEnum.Miss

    elif shot_type == ShotTypeEnum.OuterBull:
        if result <= profile.outer_bull_hit_pct:
            return ShotResultEnum.Hit
        else:
            return ShotResultEnum.Miss

    elif shot_type == ShotTypeEnum.Double:
        if result <= profile.double_hit_pct:
            return ShotResultEnum.Hit
        elif result <= (100 - profile.double_miss_outside_pct):
            return ShotResultEnum.Miss
        else:
            return ShotResultEnum.BigMiss

    else:
        raise ValueError('Unknown shot type: {}'.format(shot_type))


def get_points(current_score, dart_number, result, score_points):
    """
    Return the points scored by a shot.

    Given the current score, dart ID and shot result, get the number
    of points scored by such a shot.

    :param int current_score: current score
    :param int dart_number: dart ID (1, 2, 3)
    :param string result: shot result, as returned by get_result.
    :param dict score_points: mapping from (score, dart ID) to score tuple,
        as returned by `load_lookups`.

    :return: number of points scored.
    :rtype: int
    """
    point_tuple = score_points.get(
        (current_score, dart_number),
        DEFAULT_POINTS,
    )
    if result == ShotResultEnum.BigMiss and point_tuple[result] == 6:
        choices = [1, 3, 5, 15]
        return random.choice(choices)
    return point_tuple[result]


class DartThrow:

    def __init__(
            self,
            start_score,
            dart_number,
            profile,
            score_shot_types,
            score_points,
            ):
        log.debug('Score is {}, dart id is {}'.format(start_score, dart_number))
        self.start_score = start_score
        self.dart_number = dart_number
        self.shot_type = get_shot_type(
            start_score,
            dart_number,
            score_shot_types,
        )
        log.debug('Aiming for {}'.format(self.shot_type.name))
        self.shot_result = get_result(self.shot_type, profile)
        log.debug('Shot {}!'.format(self.shot_result.name))
        self.points_scored = get_points(
            start_score,
            dart_number,
            self.shot_result,
            score_points,
        )
        log.debug('Points scored: {}'.format(self.points_scored))


class ThreeDartStats:

    def __init__(self, *dart_throws):
        self.n_darts = len(dart_throws)
        self.shot_types = [x.shot_type for x in dart_throws]
        self.shot_results = [x.shot_result for x in dart_throws]
        self.points_scored = [x.points_scored for x in dart_throws]


def throw_dart(
        current_score,
        dart_number,
        profile,
        score_shot_types,
        score_points,
        ):
    """
    Simulate the throwing of a dart at a particular score.

    Returns the number of points scored by the dart.

    :param int current_score: current score (before throwing the dart)
    :param int dart_number: dart ID (1, 2, 3)

    :param profile: shot profile
    :type profile: :py:class:`~darts.models.Profile`

    :param dict score_shot_types: mapping from (score, dart_number) to
        shot types, as returned by `~load_lookups`
    :param dict score_points: mapping from (score, dart ID) to score tuple,
        as returned by `load_lookups`.

    :return: number of points scored.
    :rtype: int
    """
    shot_type = get_shot_type(current_score, dart_number, score_shot_types)
    result = get_result(shot_type, profile)
    points = get_points(current_score, dart_number, result, score_points)
    return (dart_number, shot_type, result, points)


def throw_three_darts(current_score, profile, score_shot_types, score_points):
    """
    Simulate throwing three darts.

    Encapsulates the logic of winning if score reaches 0 after any dart,
    or busting if score is either 1 or less than zero.

    Returns a tuple containing:

    - the new score after throwing three darts
    - the three dart total
    - the number of darts thrown

    :param int current_score: current score (before throwing the dart)

    :param profile: shot profile
    :type profile: :py:class:`~darts.models.Profile`

    :param dict score_shot_types: mapping from (score, dart_number) to
        shot types, as returned by `~load_lookups`
    :param dict score_points: mapping from (score, dart ID) to score tuple,
        as returned by `load_lookups`.

    :return: the new score, three dart total, and number of darts thrown.
    :rtype: Tuple[int, int, int]
    """

    new_score = current_score

    three_dart_total = 0
    three_dart_stats = []

    log.debug('Starting three dart turn on {} points'.format(current_score))
    for dart_id in [1, 2, 3]:
        dart_throw = DartThrow(
            new_score,
            dart_id,
            profile,
            score_shot_types,
            score_points,
        )

        new_score = new_score - dart_throw.points_scored
        three_dart_stats.append(dart_throw)
        three_dart_total += dart_throw.points_scored

        if new_score > 1:
            # More darts to throw
            continue

        elif new_score == 0:
            return (new_score, ThreeDartStats(*three_dart_stats))

        else:
            # score is either 1 or < 0, so bust.
            return (new_score, ThreeDartStats(*[]))

    return (new_score, ThreeDartStats(*three_dart_stats))


class LegStats:

    def __init__(self, total, *three_dart_stats):
        self.three_dart_totals = [
            sum(x.points_scored) for x in three_dart_stats
        ]
        self.num_180s = self.three_dart_totals.count(180)
        self.all_darts = list(self.create_rows(*three_dart_stats))
        n_darts = len([x for dart in self.all_darts for x in dart])
        self.three_dart_average = 3.0 * float(total) / float(n_darts)

    def create_rows(self, *three_dart_stats):
        for darts in three_dart_stats:
            rows = zip(darts.shot_types, darts.shot_results, darts.points_scored)  # noqa
            yield [(row[0].value, row[1].value, row[2]) for row in rows]

    def as_dict(self):
        return dict(
            three_dart_totals=self.three_dart_totals,
            three_dart_average=self.three_dart_average,
            num_180s=self.num_180s,
            all_darts=[[
                v.value if isinstance(v, enum.Enum) else v
                for v in dart
            ] for dart in self.all_darts]
        )


def simulate_leg(profile, score_shot_types, score_points, total=501):
    """
    Simulate a leg of darts.

    Returns every three dart total.

    :param profile: shot profile
    :type profile: :py:class:`~darts.models.Profile`

    :param dict score_shot_types: mapping from (score, dart_number) to
        shot types, as returned by `~load_lookups`
    :param dict score_points: mapping from (score, dart ID) to score tuple,
        as returned by `load_lookups`.
    :param int total: Total required to win a leg of darts (default: 501).

    :return: List of lists holdingthree dart totals.
    :rtype: List[int]
    """
    all_three_dart_stats = []
    current_score = total
    while current_score > 0:
        current_score, three_dart_stats = throw_three_darts(
            current_score,
            profile,
            score_shot_types,
            score_points,
        )
        all_three_dart_stats.append(three_dart_stats)

    return LegStats(total, *all_three_dart_stats)


def simulate_profile(
        profile,
        score_shot_types,
        score_points,
        iterations=1000,
        total=501,
        ):
    """
    Simulate a profile by simulating lots of legs.

    :param profile: shot profile
    :type profile: :py:class:`~darts.models.Profile`

    :param dict score_shot_types: mapping from (score, dart_number) to
        shot types, as returned by `~load_lookups`
    :param dict score_points: mapping from (score, dart ID) to score tuple,
        as returned by `load_lookups`.
    :param int iterations: Number of iterations to run (default: 10000).
    :param int total: Total required to win a leg of darts (default: 501).

    """
    legs = []
    for i in xrange(iterations):
        leg = simulate_leg(profile, score_shot_types, score_points, total)
        legs.append(leg)
        if i % 1000 == 0:
            print('ran %s iterations' % i)

    return legs

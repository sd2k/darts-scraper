"""
Simulations of 1-player matches.
"""
import random

from darts import models


DEFAULT_SHOT_TYPE = 'treble'
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
        score_shot_types[key] = row.shot_type
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

    :return: shot outcome - 0 for hit, 1 for miss (or miss inside),
        2 for big miss (or miss outside)
    :rtype: int
    """

    if shot_type == 'single':
        return 0

    result = 100 * random.random()

    if shot_type == 'treble':
        if result <= profile.treble_hit_pct:
            return 0
        elif result <= (100 - profile.treble_big_miss_pct):
            return 1
        else:
            return 2

    elif shot_type == 'bull':
        if result <= profile.bullseye_hit_pct:
            return 0
        else:
            return 1

    elif shot_type == 'outer_bull':
        if result <= profile.outer_bull_hit_pct:
            return 0
        else:
            return 1

    elif shot_type == 'double':
        if result <= profile.double_hit_pct:
            return 0
        elif result <= (100 - profile.double_miss_outside_pct):
            return 1
        else:
            return 2

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
    return point_tuple[result]


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
    return points


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

    for dart in [1, 2, 3]:
        score = throw_dart(
            current_score,
            dart,
            profile,
            score_shot_types,
            score_points,
        )

        new_score = current_score - score
        if new_score > 1:
            # More darts to throw
            three_dart_total += score

        elif new_score == 0:
            return (new_score, three_dart_total)

        else:
            # score is either 1 or < 0, so bust.
            return (current_score, 0.0)

    return (new_score, three_dart_total)


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

    :return: List of three dart totals.
    :rtype: List[int]
    """
    three_dart_totals = []
    current_score = total
    while current_score > 0:
        current_score, three_dart_total = throw_three_darts(
            current_score,
            profile,
            score_shot_types,
            score_points,
        )
        three_dart_totals.append(three_dart_total)

    return three_dart_totals


def simulate_profile(
        profile,
        score_shot_types,
        score_points,
        iterations=10000,
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
    three_dart_totals = []
    for i in xrange(iterations):
        sim = simulate_leg(profile, score_shot_types, score_points, total)
        three_dart_totals.append(sim)
        if i % 1000 == 0:
            print('ran %s iterations' % i)

    return three_dart_totals

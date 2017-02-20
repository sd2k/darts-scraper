import random

import numpy as np

from darts import models


DEFAULT_SHOT_TYPE = 'treble'
"Shot type to use if score doesn't appear in lookup"

DEFAULT_POINTS = (60, 20, 6)
"Points tuple to use if score doesn't appear in lookup"


def load_lookups(session):
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
    return score_shot_types.get(
        (current_score, dart_number),
        DEFAULT_SHOT_TYPE,
    )


def get_result(shot_type, profile):
    """
    Return 0 for hit, 1 for miss OR miss inside,
    2 for big miss OR miss outside.
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
    shot_type = get_shot_type(current_score, dart_number, score_shot_types)
    result = get_result(shot_type, profile)
    points = get_points(current_score, dart_number, result, score_points)
    return points


def throw_three_darts(current_score, profile, score_shot_types, score_points):
    """
    Returns (new_score, three_dart_total, n_darts).
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
    """
    three_dart_totals = []
    for i in xrange(iterations):
        sim = simulate_leg(profile, score_shot_types, score_points, total)
        three_dart_totals.extend(sim)
        if i % 1000 == 0:
            print('ran %s iterations' % i)

    return three_dart_totals

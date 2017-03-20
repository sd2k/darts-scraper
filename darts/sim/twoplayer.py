from functools import partial
import logging

from darts.models import LegStats, ShotResultEnum, ShotTypeEnum
from . import oneplayer


log = logging.getLogger(__name__)


def simulate_leg(
        profile_a,
        profile_b,
        score_shot_types,
        score_points,
        a_first=True,
        total=501,
        ):

    all_pa_stats, all_pb_stats = [], []
    pa_score, pb_score = total, total

    throw_three_darts_a, throw_three_darts_b = [partial(
        oneplayer.throw_three_darts,
        profile=p,
        score_shot_types=score_shot_types,
        score_points=score_points,
    ) for p in (profile_a, profile_b)]

    while pa_score > 0 and pb_score > 0:
        if a_first:
            pa_score, pa_stats = throw_three_darts_a(pa_score)
            all_pa_stats.append(pa_stats)
            if pa_score <= 0:
                winner = 'a'
                break
            pb_score, pb_stats = throw_three_darts_b(pb_score)
            all_pb_stats.append(pb_stats)
        else:
            pb_score, pb_stats = throw_three_darts_b(pb_score)
            all_pb_stats.append(pb_stats)
            if pb_score <= 0:
                winner = 'b'
                break
            pa_score, pa_stats = throw_three_darts_a(pa_score)
            all_pa_stats.append(pa_stats)
        a_first = not a_first

    return winner, LegStats(*all_pa_stats), LegStats(*all_pb_stats)


class MatchStats:

    def __init__(self, profiles, wins, scores, all_legs):
        self.profiles = profiles
        self.wins = wins
        self.scores = scores
        self.winner = profiles[0] if scores[0] > scores[1] else profiles[1]


def simulate_match_play(
        profile_a,
        profile_b,
        score_shot_types,
        score_points,
        total_legs=7,
        a_first=True,
        a_handicap=0,
        b_handicap=0,
        ):

    # List of (winner, LegStats - profile A, LegStats - profile B) tuples
    legs = []

    a_wins, b_wins = 0, 0

    while a_wins < total_legs and b_wins < total_legs:
        leg = simulate_leg(
            profile_a,
            profile_b,
            score_shot_types,
            score_points,
        )
        log.debug('Leg winner: {}'.format(
            profile_a.name if leg[0] == 'a' else profile_b.name
        ))
        legs.append(leg)
        if leg[0] == 'a':
            a_wins += 1
        else:
            b_wins += 1

    a_score = a_wins + a_handicap
    b_score = b_wins + b_handicap

    return MatchStats(
        profiles=(profile_a, profile_b),
        wins=(a_wins, b_wins),
        scores=(a_score, b_score),
        all_legs=legs,
    )


def simulate_match(
        profile_a,
        profile_b,
        score_shot_types,
        score_points,
        match_type,
        a_first=True,
        a_handicap=0,
        b_handicap=0,
        ):
    """
    Simulate a match between two players represented by the given profiles.

    Returns an object containing the stats and darts thrown in the match.
    """

    if match_type == '':
        pass

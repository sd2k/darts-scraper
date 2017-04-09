from functools import partial
import logging

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
            if pb_score <= 0:
                winner = 'b'
                break
        else:
            pb_score, pb_stats = throw_three_darts_b(pb_score)
            all_pb_stats.append(pb_stats)
            if pb_score <= 0:
                winner = 'b'
                break
            pa_score, pa_stats = throw_three_darts_a(pa_score)
            all_pa_stats.append(pa_stats)
            if pa_score <= 0:
                winner = 'a'
                break
        a_first = not a_first

    return (
        winner,
        oneplayer.LegStats(total, *all_pa_stats),
        oneplayer.LegStats(total, *all_pb_stats),
    )


class MatchStats:

    def __init__(self, profiles, wins, scores, all_legs):
        self.profiles = profiles
        self.wins = wins
        self.scores = scores
        self.winner = (
            profiles[0] if scores[0] > scores[1] else
            profiles[1] if scores[1] > scores[0] else
            'draw'
        )
        self.all_legs = all_legs

    def as_dict(self):
        return dict(
            winner=(
                'a' if self.winner == self.profiles[0] else
                'b' if self.winner == self.profiles[1] else
                'draw'
            ),
            scores=self.scores,
            # all_legs=[leg.as_dict() for leg in self.all_legs],
        )


def simulate_match_play(
        profile_a,
        profile_b,
        score_shot_types,
        score_points,
        legs_to_win=7,
        a_first=True,
        a_handicap=0,
        b_handicap=0,
        total_legs=None,
        ):
    """
    Note - if total_legs = 12, this is 'Premier League' play.
    """

    # List of (winner, LegStats - profile A, LegStats - profile B) tuples
    legs = []

    a_wins, b_wins = 0, 0

    while a_wins < legs_to_win and b_wins < legs_to_win:
        leg = simulate_leg(
            profile_a,
            profile_b,
            score_shot_types,
            score_points,
        )
        log.debug('Leg winner: {}'.format(leg[0]))
        legs.append(leg)
        if leg[0] == 'a':
            a_wins += 1
        else:
            b_wins += 1
        if total_legs is not None and len(legs) >= total_legs:
            break

    a_score = a_wins + a_handicap
    b_score = b_wins + b_handicap

    return MatchStats(
        profiles=(profile_a, profile_b),
        wins=(a_wins, b_wins),
        scores=(a_score, b_score),
        all_legs=legs,
    )


class SetStats:

    def __init__(self, profiles, wins, all_legs):
        self.profiles = profiles
        self.wins = wins
        self.all_legs = all_legs
        self.winner = profiles[0] if wins[0] > wins[1] else profiles[1]


def simulate_set(
        profile_a,
        profile_b,
        score_shot_types,
        score_points,
        a_first=True,
        ):
    # List of (winner, LegStats - profile A, LegStats - profile B) tuples
    legs = []
    LEGS_TO_WIN = 3

    a_wins, b_wins = 0, 0

    while a_wins < LEGS_TO_WIN and b_wins < LEGS_TO_WIN:
        leg = simulate_leg(
            profile_a,
            profile_b,
            score_shot_types,
            score_points,
            a_first,
        )
        log.debug('Leg winner: {}'.format(leg[0]))
        legs.append(leg)
        if leg[0] == 'a':
            a_wins += 1
        else:
            b_wins += 1
        a_first = not a_first

    return SetStats(
        profiles=(profile_a, profile_b),
        wins=(a_wins, b_wins),
        all_legs=legs,
    )


def simulate_set_play(
        profile_a,
        profile_b,
        score_shot_types,
        score_points,
        total_sets=5,
        a_first=True,
        a_handicap=0,
        b_handicap=0,
        ):

    sets = []
    a_sets, b_sets = 0, 0

    while a_sets < total_sets and b_sets < total_sets:
        s = simulate_set(
            profile_a,
            profile_b,
            score_shot_types,
            score_points,
        )
        log.debug('Set winner: {}'.format(s.winner))
        sets.append(s)
        if s.winner == profile_a:
            a_sets += 1
        else:
            b_sets += 1

        a_first = not a_first

    a_score = a_sets + a_handicap
    b_score = b_sets + b_handicap

    return MatchStats(
        (profile_a, profile_b),
        (a_sets, b_sets),
        (a_score, b_score),
        sets,
    )


def simulate_match(match_type, iterations=1000, **kwargs):
    """
    Simulate a match between two players represented by the given profiles.

    Returns an object containing the stats and darts thrown in the match.
    """

    if match_type == 'match_play':
        match_fn = simulate_match_play
    elif match_type == 'set_play':
        match_fn = simulate_set_play
    elif match_type == 'premier_league':
        # Always 12 legs in a Premier League match.
        kwargs['total_legs'] = 12
        match_fn = simulate_match_play

    matches = []

    a_first = kwargs.pop('a_first', True)

    for i in xrange(iterations):
        match = match_fn(a_first=a_first, **kwargs)
        a_first = not a_first
        matches.append(match)
        if i % 100 == 0 and i > 0:
            log.info('ran %s iterations' % i)

    return matches

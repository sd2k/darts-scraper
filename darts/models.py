# -*- coding: utf-8 -*-
import collections
import enum

from cached_property import cached_property
import numpy as np
from sqlalchemy import (
    Boolean,
    Column,
    Date,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Integer,
    Numeric,
    String,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import backref, relationship
from sqlalchemy.sql import func

from darts.db import Base


class Tournament(Base):

    __tablename__ = 'tournaments'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    last_updated = Column(DateTime, default=func.now())

    events = relationship('Event', back_populates='tournaments')

    def __repr__(self):
        return "<Tournament(id='%s', name='%s')>" % (
            self.id,
            self.name
        )

    def __str__(self):
        return self.name


def generate_name(context):
    return '{} {}'.format(
        context.current_parameters['year'],
        context.connection.execute(
            'SELECT name FROM tournament WHERE id = %s',
            int(context.current_parameters['tournament_id'])
        ).scalar() or 'Unknown Tournament'
    )


class Event(Base):

    __tablename__ = 'events'

    id = Column(Integer, primary_key=True)
    tournament_id = Column(Integer, ForeignKey('tournaments.id'))
    always_check = Column(Boolean, default=False, nullable=True)
    name = Column(String, default=generate_name)
    year = Column(Integer)
    category = Column(String, nullable=True)
    prize_fund = Column(Integer, nullable=True)
    winner_player_id = Column(Integer, ForeignKey('players.id'))
    venue = Column(String, nullable=True)
    tv_coverage = Column(String, nullable=True)
    sponsor = Column(String, nullable=True)
    last_updated = Column(DateTime, default=func.now())

    tournaments = relationship('Tournament', back_populates='events')
    matches = relationship('Match', back_populates='event')
    fixtures = relationship('Fixture', back_populates='event')

    def __repr__(self):
        return "<Event(id='%s', name='%s', tournament_id='%s')>" % (
            self.id,
            self.name,
            self.tournament_id
        )

    def __str__(self):
        return "%s (%s)" % (self.name, self.year)


class Player(Base):

    __tablename__ = 'players'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    dob = Column(Date)
    last_updated = Column(DateTime, default=func.now())

    pdc_ranking = Column(Integer, nullable=True)
    red_dragon_ranking = Column(Integer, nullable=True)
    ddb_ranking = Column(Integer, nullable=True)
    ddb_popularity = Column(Integer, nullable=True)

    career_earnings = Column(Float, nullable=True)
    career_9_darters = Column(Integer, nullable=True)

    match_results = relationship(
        'MatchResult',
        back_populates='player',
        lazy='dynamic'
    )
    fixtures = association_proxy('fixture_players', 'fixture')

    def __repr__(self):
        return "<Player(id='%s', name='%s', pdc_ranking='%s')>" % (
            self.id,
            self.name,
            self.pdc_ranking
        )

    def __str__(self):
        return self.name


class Match(Base):

    __tablename__ = 'matches'

    id = Column(Integer, primary_key=True)
    date = Column(Date)
    event_id = Column(Integer, ForeignKey('events.id'))
    last_updated = Column(DateTime, default=func.now())

    event = relationship('Event', back_populates='matches')

    match_results = relationship(
        'MatchResult',
        back_populates='match',
        lazy='dynamic'
    )

    @hybrid_property
    def name(self):
        return str(self)

    def __repr__(self):
        return "<Match(id='%s', date='%s', event='%s', players='%s')>" % (
            self.id,
            self.date,
            self.event_id,
            ' vs '.join(x.player.name for x in self.match_results)
        )

    def __str__(self):
        try:
            return "{} vs {} - {date}".format(
                *([result.player for result in self.match_results][:2]),
                date=self.date
            )
        except IndexError:
            return repr(self)


class MatchResult(Base):

    __tablename__ = 'match_results'

    player_id = Column(Integer, ForeignKey('players.id'), primary_key=True)
    match_id = Column(Integer, ForeignKey('matches.id'), primary_key=True)
    score = Column(Integer)
    average = Column(Float)
    oneeighties = Column(Integer)
    high_checkout = Column(Integer)
    checkout_percent = Column(Float)
    checkout_chances = Column(Integer)
    last_updated = Column(DateTime, default=func.now())

    player = relationship('Player', back_populates='match_results')
    match = relationship('Match', back_populates='match_results')

    @property
    def vs_player(self):
        try:
            vs_player = (
                self.match.match_results
                .filter(MatchResult.player_id != self.player_id)
                .first()
                .player.name
            )
        except AttributeError:
            vs_player = ''
        return vs_player

    def __repr__(self):
        return "<MatchResult(player_id='%s', vs='%s', score='%s')>" % (
            self.player_id,
            self.vs_player,
            self.score,
        )


class Fixture(Base):

    """
    A fixture is an as-yet unplayed match.

    As matches get played, fixtures should be removed.
    """

    __tablename__ = 'fixtures'

    id = Column(Integer, primary_key=True)
    event_id = Column(Integer, ForeignKey('events.id'))
    date = Column(Date)

    event = relationship('Event')

    players = association_proxy(
        'fixture_players',
        'player',
        creator=lambda i: FixturePlayer(player=i)
    )

    def __repr__(self):
        return "<Fixture(event='%s', date='%s', players='%s')>" % (
            self.event_id,
            self.date,
            ' vs '.join(
                player.name for player in self.players if player is not None
            )
        )


class FixturePlayer(Base):

    __tablename__ = 'fixture_players'

    player_id = Column(Integer, ForeignKey('players.id'), primary_key=True)
    fixture_id = Column(Integer, ForeignKey('fixtures.id'), primary_key=True)

    player = relationship(
        'Player',
        backref=backref('fixture_players', cascade='all, delete-orphan')
    )
    fixture = relationship(
        'Fixture',
        backref=backref('fixture_players', cascade='all, delete-orphan')
    )

    def __repr__(self):
        return "<FixturePlayer(fixture='%s', player='%s')>" % (
            self.fixture_id,
            self.player.name,
        )


class Profile(Base):

    __tablename__ = 'profiles'

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)

    treble_hit_pct = Column(Numeric(4, 2), nullable=False)
    treble_miss_pct = Column(Numeric(4, 2), nullable=False)
    treble_big_miss_pct = Column(Numeric(4, 2), nullable=False)

    bullseye_hit_pct = Column(Numeric(4, 2), nullable=False)
    bullseye_miss_pct = Column(Numeric(4, 2), nullable=False)

    outer_bull_hit_pct = Column(Numeric(4, 2), nullable=False)
    outer_bull_miss_pct = Column(Numeric(4, 2), nullable=False)

    single_hit_pct = 100.00

    double_hit_pct = Column(Numeric(4, 2), nullable=False)
    double_miss_inside_pct = Column(Numeric(4, 2), nullable=False)
    double_miss_outside_pct = Column(Numeric(4, 2), nullable=False)

    def __repr__(self):
        return "<Profile(name='%s')>" % self.name

    def __str__(self):
        return self.name


class DartEnum(enum.IntEnum):
    one = 1
    two = 2
    three = 3


class ShotResultEnum(enum.IntEnum):
    Hit = 0
    Miss = 1
    BigMiss = 2


class ShotTypeEnum(enum.Enum):
    Treble = 'treble'
    Double = 'double'
    Single = 'single'
    Bull = 'bull'
    OuterBull = 'outer_bull'


class ScoreLookup(Base):

    __tablename__ = 'score_lookups'

    score = Column(Integer, primary_key=True)
    dart = Column(Enum(DartEnum, name='dart_numbers'), primary_key=True)

    shot_type = Column(Enum(
        'single',
        'treble',
        'bull',
        'outer_bull',
        'double',
        name='shot_types',
    ), nullable=False)

    hit_points = Column(Integer, nullable=False)
    miss_points = Column(Integer, nullable=True)
    big_miss_points = Column(Integer, nullable=True)

    def __repr__(self):
        return "<ScoreLookup(score='%s', dart='%s')>" % (
            self.score,
            self.dart,
        )

    def __str__(self):
        return repr(self)


class PlayerSimulation(Base):

    __tablename__ = 'player_simulations'

    id = Column(Integer, primary_key=True)
    profile_id = Column(Integer, ForeignKey('profiles.id'))
    iterations = Column(Integer, nullable=False, default=10000)
    results = Column(JSONB, nullable=False)

    profile = relationship('Profile')

    @cached_property
    def leg_averages(self):
        return [leg['three_dart_average'] for leg in self.results]

    @cached_property
    def leg_180s(self):
        return [leg['num_180s'] for leg in self.results]

    @cached_property
    def three_dart_average(self):
        return np.mean(self.leg_averages)

    @cached_property
    def three_dart_std_dev(self):
        return np.std(self.leg_averages)

    @cached_property
    def avg_180s(self):
        return np.mean(self.leg_180s)

    @cached_property
    def std_180s(self):
        return np.std(self.leg_180s)

    @cached_property
    def leg_darts(self):
        return [leg['all_darts'] for leg in self.results]

    @cached_property
    def three_dart_average_hist(self):
        hist = np.histogram(self.leg_averages, bins='auto')
        ticks = [
            str(round(edge, 1)) for edge in hist[1]
        ]
        labels = [
            '-'.join(x) for x in zip(ticks, ticks[1:])
        ]
        return hist[0].tolist(), labels

    @cached_property
    def three_dart_scores(self):
        counter = collections.Counter(
            sum(dart[2] for dart in three_darts)
            for leg in self.leg_darts
            for three_darts in leg
        )
        scores = []
        labels = []
        for x in xrange(181):
            scores.append(counter[x])
            labels.append(x)

        return scores, labels

    @cached_property
    def all_darts(self):
        def darts():
            for leg_id, leg in enumerate(self.results):
                score = 501
                for three_darts in leg['all_darts']:
                    for dart_id, dart in enumerate(three_darts):
                        yield (
                            leg_id + 1,
                            score,
                            dart_id + 1,
                            ShotTypeEnum(dart[0]).name,
                            ShotResultEnum(dart[1]).name,
                            dart[2],
                        )
                        score -= dart[2]
        return list(darts())

    def __repr__(self):
        return "<Simulation(profile_id='%s', iterations='%s')>" % (
            self.profile_id,
            self.iterations,
        )

    def __str__(self):
        return "Simulation of profile {} ({} iterations)".format(
            self.profile.name,
            self.iterations,
        )

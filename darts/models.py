# -*- coding: utf-8 -*-

from sqlalchemy import (
    Boolean,
    Column,
    Date,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    Numeric,
    String,
)
from sqlalchemy.orm import backref, relationship
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.ext.hybrid import hybrid_property
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
    name = Column(String)

    treble_hit_pct = Column(Numeric(4, 2))
    treble_miss_pct = Column(Numeric(4, 2))
    treble_big_miss_pct = Column(Numeric(4, 2))

    bullseye_hit_pct = Column(Numeric(4, 2))
    bullseye_miss_pct = Column(Numeric(4, 2))

    outer_bull_hit_pct = Column(Numeric(4, 2))
    outer_bull_miss_pct = Column(Numeric(4, 2))

    single_hit_pct = 100.00

    double_hit_pct = Column(Numeric(4, 2))
    double_miss_inside_pct = Column(Numeric(4, 2))
    double_miss_outside_pct = Column(Numeric(4, 2))

    def __repr__(self):
        return "<Profile(name='%s')>" % self.name

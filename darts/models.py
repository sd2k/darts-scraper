# -*- coding: utf-8 -*-

from sqlalchemy import (
    create_engine,
    select,
    Column,
    Date,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
)
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func

from darts import settings


Base = declarative_base()
engine = create_engine(settings.DATABASE_URL)
Session = sessionmaker(bind=engine)


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


def generate_name(context):
    return '{} {}'.format(
        context.current_parameters['year'],
        select(Tournament.name).where(
            Tournament.id == context.current_parameters['tournament_id']
        )
    )


class Event(Base):

    __tablename__ = 'events'

    id = Column(Integer, primary_key=True)
    tournament_id = Column(Integer, ForeignKey('tournaments.id'))
    name = Column(String, default=generate_name)
    year = Column(Integer)
    venue = Column(Integer, nullable=True)
    tv_coverage = Column(String, nullable=True)
    sponsor = Column(String, nullable=True)
    last_updated = Column(DateTime, default=func.now())

    tournaments = relationship('Tournament', back_populates='events')
    matches = relationship('Match', back_populates='events')

    def __repr__(self):
        return "<Event(id='%s', name='%s', tournament_id='%s')>" % (
            self.id,
            self.name,
            self.tournament_id
        )


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
        back_populates='player'
    )

    def __repr__(self):
        return "<Player(id='%s', name='%s', pdc_ranking='%s')>" % (
            self.id,
            self.name,
            self.pdc_ranking
        )


class Match(Base):

    __tablename__ = 'matches'

    id = Column(Integer, primary_key=True)
    date = Column(Date)
    event_id = Column(Integer, ForeignKey('events.id'))
    last_updated = Column(DateTime, default=func.now())

    events = relationship('Event', back_populates='matches')

    match_results = relationship(
        'MatchResult',
        back_populates='match',
        lazy='dynamic'
    )

    def __repr__(self):
        return "<Match(id='%s', date='%s', event='%s', players='%s')>" % (
            self.id,
            self.date,
            self.event_id,
            ' vs '.join([x.player.name for x in self.match_results])
        )


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

    def __repr__(self):
        return "<MatchResult(player='%s', vs='%s', score='%s')>" % (
            self.player.name,
            self.match.match_results.
               filter(MatchResult.player_id != self.player_id).
               first().player.name,
            self.score
        )

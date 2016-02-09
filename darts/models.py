# -*- coding: utf-8 -*-

from sqlalchemy import (
    create_engine,
    select,
    Column,
    Date,
    Float,
    ForeignKey,
    Integer,
    String,
    Table,
)
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.engine.url import URL

from darts import settings


url = URL(**settings.DATABASE_SETTINGS)

engine = create_engine(url)

Base = declarative_base()


class Player(Base):

    __tablename__ = 'players'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    dob = Column(Date)

    pdc_ranking = Column(Integer, nullable=True)
    red_dragon_ranking = Column(Integer, nullable=True)
    ddb_ranking = Column(Integer, nullable=True)
    ddb_popularity = Column(Integer, nullable=True)

    career_earnings = Column(Float, nullable=True)
    career_9_darters = Column(Integer, nullable=True)

    matches = relationship(
        'Match',
        secondary='match_players',
        back_populates='players'
    )

    def __repr__(self):
        return "<Player(id='%s', name='%s', pdc_ranking='%s')>" % (
            self.id,
            self.name,
            self.pdc_ranking
        )


class Tournament(Base):

    __tablename__ = 'tournaments'

    id = Column(Integer, primary_key=True)
    name = Column(String)

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

    tournaments = relationship('Tournament', back_populates='events')
    matches = relationship('Match', back_populates='events')

    def __repr__(self):
        return "<Event(id='%s', name='%s', tournament_id='%s')>" % (
            self.id,
            self.name,
            self.tournament_id
        )


class Match(Base):

    __tablename__ = 'matches'

    id = Column(Integer, primary_key=True)
    date = Column(Date)
    event_id = Column(Integer, ForeignKey('events.id'))

    events = relationship('Event', back_populates='matches')

    players = relationship(
        'Player',
        secondary='match_players',
        back_populates='matches'
    )

    def __repr__(self):
        return "<Match(id='%s', date='%s', event='%s', players='%s')>" % (
            self.id,
            self.date,
            self.event_id,
            ' vs '.join([x.name for x in self.players])
        )


match_players = Table(
    'match_players',
    Base.metadata,
    Column('player_id', Integer, ForeignKey('players.id')),
    Column('match_id', Integer, ForeignKey('matches.id'))
)

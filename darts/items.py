# -*- coding: utf-8 -*-

from scrapy import Item, Field


class Tournament(Item):

    id = Field()
    name = Field()


class Event(Item):

    id = Field()
    tournament_id = Field()
    name = Field()
    year = Field()
    venue = Field()
    tv_coverage = Field()
    sponsor = Field()


class Player(Item):

    id = Field()
    name = Field()
    dob = Field()

    pdc_ranking = Field()
    red_dragon_ranking = Field()
    ddb_ranking = Field()
    ddb_popularity = Field()

    career_earnings = Field()
    career_9_darters = Field()


class Match(Item):

    id = Field()
    date = Field()
    event_id = Field()


class MatchResult(Item):

    player_name = Field()
    match_id = Field()
    score = Field()
    average = Field()
    oneeighties = Field()
    high_checkout = Field()
    checkout_percent = Field()
    checkout_chances = Field()

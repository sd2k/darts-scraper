# -*- coding: utf-8 -*-

from scrapy import Item, Field
from scrapy.loader.processors import TakeFirst


def TakeFirstField():
    return Field(output_processor=TakeFirst())


class Tournament(Item):

    id = TakeFirstField()
    name = TakeFirstField()


class Event(Item):

    id = TakeFirstField()
    tournament_id = TakeFirstField()
    name = TakeFirstField()
    year = TakeFirstField()
    category = TakeFirstField()
    prize_fund = TakeFirstField()
    winner_player_id = TakeFirstField()
    venue = TakeFirstField()
    tv_coverage = TakeFirstField()
    sponsor = TakeFirstField()


class Player(Item):

    id = Field()
    name = TakeFirstField()
    dob = TakeFirstField()

    pdc_ranking = TakeFirstField()
    red_dragon_ranking = TakeFirstField()
    ddb_ranking = TakeFirstField()
    ddb_popularity = TakeFirstField()

    career_earnings = TakeFirstField()
    career_9_darters = TakeFirstField()


class Match(Item):

    id = TakeFirstField()
    date = TakeFirstField()
    event_id = TakeFirstField()


class MatchResult(Item):

    player_id = TakeFirstField()
    match_id = TakeFirstField()
    score = TakeFirstField()
    average = TakeFirstField()
    oneeighties = TakeFirstField()
    high_checkout = TakeFirstField()
    checkout_info = TakeFirstField()

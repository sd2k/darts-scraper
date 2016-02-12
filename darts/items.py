# -*- coding: utf-8 -*-

from scrapy import Item, Field
from scrapy.loader.processors import TakeFirst


class Tournament(Item):

    id = Field()
    name = Field()


class Event(Item):

    id = Field()
    tournament_id = Field()
    name = Field()
    year = Field()
    category = Field()
    prize_fund = Field()
    winner_player_id = Field()
    venue = Field()
    tv_coverage = Field()
    sponsor = Field()


class Player(Item):

    id = Field()
    name = Field(output_processor=TakeFirst())
    dob = Field(output_processor=TakeFirst())

    pdc_ranking = Field(output_processor=TakeFirst())
    red_dragon_ranking = Field(output_processor=TakeFirst())
    ddb_ranking = Field(output_processor=TakeFirst())
    ddb_popularity = Field(output_processor=TakeFirst())

    career_earnings = Field(output_processor=TakeFirst())
    career_9_darters = Field(output_processor=TakeFirst())


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

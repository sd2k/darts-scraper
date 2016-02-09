# -*- coding: utf-8 -*-

from scrapy import Item, Field


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


class Tournament(Item):

    id = Field()
    name = Field()


class Event(Item):

    id = Field()
    tournament_id = Field()
    year = Field()
    venue = Field()
    tv_coverage = Field()
    sponsor = Field()


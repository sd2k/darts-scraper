# -*- coding: utf-8 -*-
import scrapy


class PlayerstatsSpider(scrapy.Spider):
    name = "playerstats"
    allowed_domains = ["http://www.dartsdatabase.co.uk/PlayerStats.aspx"]
    start_urls = (
        'http://www.http://www.dartsdatabase.co.uk/PlayerStats.aspx/',
    )

    def parse(self, response):
        pass

# -*- coding: utf-8 -*-
import scrapy


class RankingsSpider(scrapy.Spider):
    name = "rankings"
    allowed_domains = ["http://www.dartsdatabase.co.uk/Rankings.aspx"]
    start_urls = (
        'http://www.http://www.dartsdatabase.co.uk/Rankings.aspx/',
    )

    def parse(self, response):
        pass

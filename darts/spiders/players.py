# -*- coding: utf-8 -*-
from scrapy.linkextractors import LinkExtractor
from scrapy.loader import ItemLoader
from scrapy.loader.processors import TakeFirst
from scrapy.spiders import CrawlSpider, Rule
from scrapy.selector import Selector

from darts.items import Player


class PlayerSpider(CrawlSpider):
    name = "players"
    allowed_domains = ["dartsdatabase.co.uk"]
    start_urls = (
        'http://www.dartsdatabase.co.uk/PlayerStats.aspx?statKey=1',
    )

    rules = [
        Rule(
            LinkExtractor(allow=('PlayerDetails\.aspx',)),
            callback='parse_player'
        ),
        Rule(
            LinkExtractor(allow=('PlayerStats\.aspx\?statKey=1',))
        ),
    ]

    item_fields = dict(
        name='center/b/font/text()[1]',
        dob="table/tr/td[b/text() = 'Date Of Birth : ']/following-sibling::td[1]/b/text()",  # noqa
        pdc_ranking="table/tr/td[b/text() = 'PDC Ranking : ']/following-sibling::td[1]/b/text()",  # noqa
        red_dragon_ranking="table/tr/td[b/text() = 'Red Dragon Ranking : ']/following-sibling::td[1]/b/text()",  # noqa
        ddb_ranking="table/tr/td[b/text() = 'DDB Ranking : ']/following-sibling::td[1]/b/text()",  # noqa
        ddb_popularity="table/tr/td[b/text() = 'DDB Popularity : ']/following-sibling::td[1]/b/text()",  # noqa
        career_earnings="table/tr/td[b/text() = 'Career Earnings : ']/following-sibling::td[1]/b/text()",  # noqa
        career_9_darters="table/tr/td[b/text() = 'Career 9 Darters : ']/following-sibling::td[1]/b/text()",  # noqa
    )

    main_table_selector = '//body/form/table/tr/td/center'

    def parse_player(self, response):
        self.logger.debug('Parsing %s', response.url)

        player = Player(id=response.url.split('=')[-1])
        self.logger.debug('Loading player %s', player['id'])

        selector = Selector(response).xpath(self.main_table_selector)

        loader = ItemLoader(
            player,
            response=response,
            selector=selector,
            default_output_processor=TakeFirst()
        )
        for field, xpath in self.item_fields.iteritems():
            loader.add_xpath(field, xpath)
        yield loader.load_item()

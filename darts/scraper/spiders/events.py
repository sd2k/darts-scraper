# -*- coding: utf-8 -*-
import datetime
try:
    import urlparse
except ImportError:
    import urllib.parse as urlparse

import scrapy
from scrapy.loader import ItemLoader
from scrapy.loader.processors import TakeFirst
from scrapy.spiders import Spider
from scrapy.selector import Selector

from darts.scraper import utils
from darts.scraper.items import (
    Event,
    Fixture,
    Match,
    MatchResult,
    Tournament,
)


class EventSpider(Spider):
    name = "events"
    allowed_domains = ["dartsdatabase.co.uk"]

    def start_requests(self):
        return [
            # scrapy.Request(
            #     'http://www.dartsdatabase.co.uk/FixtureList.aspx?EventKey=7460',  # noqa
            #     callback=self.parse_event
            # ),
            scrapy.FormRequest(
                'http://www.dartsdatabase.co.uk/EventList.aspx',
                formdata={'year': '2017'},
                callback=self.parse_tournaments,
            ),
            # scrapy.FormRequest(
            #     'http://www.dartsdatabase.co.uk/EventList.aspx',
            #     formdata={'year': '2015'},
            #     callback=self.parse_tournaments,
            # ),
            # scrapy.FormRequest(
            #     'http://www.dartsdatabase.co.uk/EventList.aspx',
            #     formdata={'year': '2014'},
            #     callback=self.parse_tournaments,
            # ),
        ]

    tournament_row_xpath = 'body/form/table/tr/td/center/table/tr'
    tournament_item_fields = dict(
        name='td[2]/a/text()',
    )

    event_info_xpath = 'body/form/table/tr/td/center'
    event_item_fields = dict(
        name='h1/text()',
        venue='table/tr/td[b/text()="Venue"]/following-sibling::td[1]/text()',
        tv_coverage='table/tr/td[b/text()="TV Coverage"]/following-sibling::td[1]/text()',  # noqa
        sponsor='table/tr/td[b/text()="Sponsor"]/following-sibling::td[1]/text()',  # noqa
    )

    event_match_table_xpath = 'body/form/table/tr/td/table/tr[td/@align="right"]'  # noqa
    fixture_match_table_xpath = 'body/form/table/tr/td/center/table/tr'

    match_info_xpath = 'body/form/table/tr/td/center'
    match_item_fields = dict(
        date='h1/text()'
    )

    match_results_table_xpath = 'body/form/table/tr/td/center/table/tr'
    match_result_item_fields = dict(
        score='td[2][text()=" Score "]/{}::td/text()',
        average='td[2][text()=" Average "]/{}::td/text()',
        oneeighties='td[2][text()=" 180s "]/{}::td/text()',
        high_checkout='td[2][text()=" High Checkout "]/{}::td/text()',
        checkout_info='td[2][text()=" Checkout % "]/{}::td/text()',
    )

    def parse_tournaments(self, response):
        """
        Parse tournament information from an events listing page,
        e.g. http://www.dartsdatabase.co.uk/EventList.aspx.

        Yields a :py:class:`darts.items.Tournament` for any new tournaments,
        and a :py:class:`scrapy.Request` object for each new event of the year.
        """
        self.logger.debug('Parsing %s', response.url)

        req = dict(
            [x.split('=') for x in str(response.request.body).split('&')]
        )

        event_url_xpath = 'td[1]/a/@href'
        tournament_url_xpath = 'td[2]/a/@href'
        category_xpath = 'td[3]/a/text()'
        prize_fund_xpath = 'td[4]/a/text()'
        winner_url_xpath = 'td[5]/a/@href'

        for tourn_row in response.xpath(self.tournament_row_xpath):
            tournament_url = (
                tourn_row.xpath(tournament_url_xpath).extract_first()
            )
            if tournament_url is None:
                # First or last row of table are header / footer so no
                # url expected.
                continue
            else:
                tournament_id = tournament_url.split('=')[-1]

            if utils.is_new('tournament', tournament_id):
                self.logger.debug('New tournament found: %s', tournament_id)
                loader = ItemLoader(
                    Tournament(id=tournament_id),
                    selector=tourn_row,
                    default_output_processor=TakeFirst(),
                )
                for field, xpath in self.tournament_item_fields.items():
                    loader.add_xpath(field, xpath)
                yield loader.load_item()
            else:
                self.logger.debug('Found old tournament: %s', tournament_id)

            event_url = urlparse.urljoin(
                response.url,
                tourn_row.xpath(event_url_xpath).extract_first()
            )
            event_id = event_url.split('=')[-1]

            if utils.is_new('event', event_id, check_matches=True):
                self.logger.debug('New event found: %s', event_id)
                year = req.get('year')
                category = tourn_row.xpath(category_xpath).extract_first()
                prize_fund = tourn_row.xpath(prize_fund_xpath).extract_first()
                winner_url = tourn_row.xpath(winner_url_xpath).extract_first()
                winner_player_id = (
                    winner_url.split('=')[-1] if winner_url else None
                )
                yield scrapy.Request(
                    event_url,
                    callback=self.parse_event,
                    meta=dict(
                        tournament_id=tournament_id,
                        year=year,
                        category=category,
                        prize_fund=prize_fund,
                        winner_player_id=winner_player_id
                    )
                )
            else:
                self.logger.debug('Found old event: %s', event_id)

    def parse_event(self, response):
        """
        Parse event information from an event page,
        e.g. http://www.dartsdatabase.co.uk/EventResults.aspx?EventKey=5664.

        Yields a single :py:class:`darts.items.Event` and a
        :py:class:`scrapy.Request` object for each match of the event.
        """
        self.logger.debug('Parsing %s', response.url)

        event_id = response.url.split('=')[-1]

        if utils.is_new('event', event_id, check_matches=True):
            if utils.is_new('event', event_id):
                event = Event(
                    id=event_id,
                    tournament_id=response.meta['tournament_id'],
                    year=response.meta['year'],
                    category=response.meta['category'],
                    prize_fund=response.meta['prize_fund'],
                    winner_player_id=response.meta['winner_player_id'],
                )
                self.logger.debug('Loading event %s', event['id'])

                event_selector = Selector(response).xpath(
                    self.event_info_xpath
                )

                event_loader = ItemLoader(
                    event,
                    response=response,
                    selector=event_selector,
                    default_output_processor=TakeFirst(),
                )
                for field, xpath in self.event_item_fields.items():
                    event_loader.add_xpath(field, xpath)
                yield event_loader.load_item()

            if 'EventResults' in response.url:
                match_rows = response.xpath(self.event_match_table_xpath)
                fixture_rows = []

                left_player_xpath = 'td[1]/a/@href'
                match_url_xpath = 'td[2]/a/@href'
                right_player_xpath = 'td[3]/a/@href'
            elif 'FixtureList' in response.url:
                all_rows = response.xpath(self.fixture_match_table_xpath)
                date_xpath = 'td[1]/text()'
                left_player_xpath = 'td[2]/a/@href'
                match_url_xpath = 'td[3]/a/@href'
                right_player_xpath = 'td[4]/a/@href'

                valid_rows = [
                    row
                    for row in all_rows
                    if row.xpath(match_url_xpath).extract_first()
                ]

                match_rows = [
                    row
                    for row in valid_rows
                    if 'MatchStats' in row.xpath(match_url_xpath).extract_first()  # noqa
                ]
                fixture_rows = [
                    row
                    for row in valid_rows
                    if 'HeadToHead' in row.xpath(match_url_xpath).extract_first()  # noqa
                ]
            else:
                return

            self.logger.debug(
                '%s fixtures found on page %s',
                len(fixture_rows),
                response.url
            )

            for i, fixture_row in enumerate(fixture_rows):

                left_player_url = fixture_row.xpath(
                    left_player_xpath
                ).extract_first()
                if not left_player_url:
                    self.logger.debug(
                        'Blank row %s on page %s', i, response.url
                    )
                    continue
                left_player_id = left_player_url.split('=')[-1]

                right_player_url = fixture_row.xpath(
                    right_player_xpath
                ).extract_first()
                right_player_id = right_player_url.split('=')[-1]

                date = fixture_row.xpath(
                    date_xpath
                ).extract_first()

                fixture = Fixture(
                    event_id=event_id,
                    player_ids=[left_player_id, right_player_id],
                    date=date
                )
                yield fixture

            self.logger.debug(
                '%s matches found on page %s',
                len(match_rows),
                response.url
            )

            for i, match_row in enumerate(match_rows):
                left_player_url = match_row.xpath(
                    left_player_xpath
                ).extract_first()
                if not left_player_url:
                    self.logger.debug(
                        'Blank row %s on page %s', i, response.url
                    )
                    continue
                left_player_id = left_player_url.split('=')[-1]

                right_player_url = match_row.xpath(
                    right_player_xpath
                ).extract_first()
                right_player_id = right_player_url.split('=')[-1]

                if left_player_id and right_player_id:

                    match_url = urlparse.urljoin(
                        response.url,
                        match_row.xpath(match_url_xpath).extract_first()
                    )
                    match_id = match_url.split('=')[-1]
                    if 'HeadToHead' in match_url:
                        continue
                    if utils.is_new('match', match_id):
                        yield scrapy.Request(
                            match_url,
                            callback=self.parse_match,
                            meta=dict(
                                event_id=event_id,
                                left_player_id=left_player_id,
                                right_player_id=right_player_id,
                            )
                        )

    def parse_match(self, response):
        self.logger.debug('Parsing %s', response.url)

        match_id = response.url.split('=')[-1]

        match = Match(
            id=match_id,
            event_id=response.meta['event_id'],
            left_player_id=response.meta['left_player_id'],
            right_player_id=response.meta['right_player_id'],
        )

        match_info_selector = Selector(response).xpath(self.match_info_xpath)

        match_loader = ItemLoader(
            match,
            response=response,
            selector=match_info_selector,
            default_output_processor=TakeFirst(),
        )
        for field, xpath in self.match_item_fields.items():
            match_loader.add_xpath(field, xpath)
        yield match_loader.load_item()

        # Each tuple is a name + the xpath axis relative to the middle column
        # on the match results page.
        for result in [
                ('left', 'preceding-sibling'),
                ('right', 'following-sibling'),
                ]:
            match_result = MatchResult(
                player_id=response.meta[result[0] + '_player_id'],
                match_id=match_id,
            )

            match_result_table_selector = Selector(response).xpath(
                self.match_results_table_xpath
            )
            results_loader = ItemLoader(
                match_result,
                response=response,
                selector=match_result_table_selector,
                default_output_processor=TakeFirst()
            )
            for field, xpath in self.match_result_item_fields.items():
                results_loader.add_xpath(field, xpath.format(result[1]))
            yield results_loader.load_item()

        try:
            match_date = match_info_selector.xpath(
                self.match_item_fields['date']
            ).extract_first()

            date = datetime.datetime.strptime(match_date, '%d/%m/%Y').date()

            utils.remove_fixture(
                response.meta['left_player_id'],
                response.meta['right_player_id'],
                date
            )
        except:
            pass

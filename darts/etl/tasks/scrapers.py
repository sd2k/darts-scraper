import datetime

from luigi.parameter import IntParameter

from darts.scraper.spiders import EventSpider, PlayerSpider
from darts.etl import base, mixins


class EventScraper(
        mixins.DailyTaskMixin,
        base.ScrapySpiderBase,
        ):

    """
    Runs the Events scraper at most once per day.
    """

    year = IntParameter(default=datetime.date.today().year)

    spider = EventSpider

    @property
    def spider_kwargs(self):
        return dict(year=str(self.year))


class PlayerScraper(
        mixins.WeeklyTaskMixin,
        base.ScrapySpiderBase,
        ):

    """
    Runs the Player scraper at most once per week.
    """

    spider = PlayerSpider

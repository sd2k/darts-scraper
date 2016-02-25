from darts.scraper.spiders import EventSpider, PlayerSpider
from darts.etl import base, mixins


class EventScraper(
        mixins.DailyTaskMixin,
        base.ScrapySpiderBase,
        ):

    """
    Runs the Events scraper at most once per day.
    """

    spider = EventSpider


class PlayerScraper(
        mixins.WeeklyTaskMixin,
        base.ScrapySpiderBase,
        ):

    """
    Runs the Player scraper at most once per week.
    """

    spider = PlayerSpider

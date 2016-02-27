import textwrap

import luigi

from .views import StatsSince2015View
from darts.etl import base, mixins


class UpcomingPlayerStatsSlackReport(
        mixins.WeeklyTaskMixin,
        base.QueryToSlackReportBase,
        ):
    """
    Posts the latest player stats for any players in upcoming fixtures
    to Slack.
    """

    @property
    def query(self):
        return textwrap.dedent("""
            SELECT string_agg(p.name, ' vs ') OVER (PARTITION BY f.id) AS fixture_name,
                f.date AS fixture_date,
                e.name AS fixture_event,
                stats.player_name,
                stats.oneeighties,
                stats.legs,
                stats.oneeighties_per_leg,
                p.pdc_ranking,
                p.career_9_darters
            FROM fixtures AS f
            JOIN fixture_players AS fp ON f.id = fp.fixture_id
            JOIN {stats_table} AS stats ON fp.player_id = stats.player_id
            JOIN players AS p ON fp.player_id = p.id
            JOIN events AS e ON f.event_id = e.id
            WHERE f.date - CURRENT_DATE <= 7
        """).strip().format(  # noqa
            stats_table=self.input().table
        )

    def requires(self):
        return StatsSince2015View(date=self.date)


class UpcomingFixturesSlackReport(
        mixins.DailyTaskMixin,
        base.SlackReportBase,
        ):
    """
    Posts details of available odds for upcoming fixtures to Slack.
    """
    pass


class SlackReports(
        mixins.DailyTaskMixin,
        luigi.WrapperTask,
        ):

    def requires(self):
        yield UpcomingPlayerStatsSlackReport(date=self.date)
        yield UpcomingFixturesSlackReport(date=self.date)

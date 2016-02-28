import textwrap

import luigi
from scipy.stats import binom

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
            SELECT STRING_AGG(p.name, ' vs ') OVER (PARTITION BY f.id) AS fixture_name,
                f.date AS fixture_date,
                e.name AS fixture_event,
                stats.player_name,
                stats.oneeighties,
                stats.legs,
                stats.oneeighties_per_leg,
                CASE
                    WHEN LAG(stats.oneeighties_per_leg) OVER (PARTITION BY f.id ORDER BY p.id) IS NOT NULL
                        THEN LAG(stats.oneeighties_per_leg) OVER (PARTITION BY f.id ORDER BY p.id) ELSE
                    LEAD(stats.oneeighties_per_leg) OVER (PARTITION BY f.id ORDER BY p.id)
                    END AS opponent_oneeighties_per_leg,
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

    def transform(self, dataset):

        def calculate_pa(row, n=11):
            pa = row[6]
            pb = row[7]
            a_wins = sum(
                binom.pmf(xa + 1, n, pa) * binom.cdf(xa, n, pb)
                for xa in range(n)
            )
            return a_wins

        def calculate_pb(row, n=11):
            pa = row[6]
            pb = row[7]
            b_wins = sum(
                binom.pmf(xb + 1, n, pb) * binom.cdf(xb, n, pa)
                for xb in range(n)
            )
            return b_wins

        def calculate_p_tie(row, n=11):
            pa = row[6]
            pb = row[7]
            a_wins = sum(
                binom.pmf(xa + 1, n, pa) * binom.cdf(xa, n, pb)
                for xa in range(n)
            )
            b_wins = sum(
                binom.pmf(xb + 1, n, pb) * binom.cdf(xb, n, pa)
                for xb in range(n)
            )
            return 1 - a_wins - b_wins

        dataset.append_col(calculate_pa, header='prob_most_180s')
        dataset.append_col(calculate_pb, header='prob_opponent_most_180s')
        dataset.append_col(calculate_p_tie, header='prob_tie_most_180s')

        return dataset

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

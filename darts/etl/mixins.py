import arrow
import luigi
import records
import slacker

from darts import settings
from darts.etl import parameters


class DailyTaskMixin(object):

    date = luigi.DateParameter(default=arrow.utcnow().date())


class WeeklyTaskMixin(object):

    date = parameters.WeekParameter(
        default=(
            arrow.utcnow().floor('week') + arrow.arrow.timedelta(days=3)
        ).date()
    )


class SlackClientMixin(object):

    slack_client = slacker.Slacker(settings.SLACK_API_TOKEN)


class PostgresClientMixin(object):

    postgres_client = records.Database(settings.DATABASE_URL)

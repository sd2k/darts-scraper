import logging
import textwrap

import luigi
import luigi.postgres
import scrapy.crawler
import scrapy.settings

from darts import settings
from . import mixins, targets, utils


@property
def NotImplementedProperty():
    raise NotImplementedError


class TaskBase(luigi.Task):

    _logger = None

    @property
    def logger(self):
        if self._logger is None:
            self._logger = logging.getLogger('darts-etl-task.' + self.task_id)
        return self._logger

    @logger.setter
    def logger(self, logger):
        self._logger = logger


class ScrapySpiderBase(
        TaskBase,
        ):

    """
    Base class for classes running a Scrapy spider.
    Run details are saved in the Postgres database.

    Subclasses must define their own :attr:`spider` class.
    """

    spider = NotImplementedProperty
    'Spider to run'

    crawler_settings = dict()
    'Settings to be passed to the crawler'

    def output(self):
        return luigi.postgres.PostgresTarget(
            update_id=self.task_id,
            table=None,
            **utils.parse_pg_url(settings.DATABASE_URL)
        )

    def run(self):
        # crawler_settings = scrapy.settings.Settings(darts.settings.__dict__)
        # crawler_settings.setdict(self.crawler_settings)

        process = scrapy.crawler.CrawlerProcess(
            dict(
                LOG_LEVEL='INFO',
                ITEM_PIPELINES={
                    'darts.scraper.pipelines.ItemToDBPipeline': 300,
                }
            )
        )
        process.crawl(self.spider)
        process.start()

        self.output().touch()


class PostgresMaterialisedViewBase(TaskBase):

    """
    Base class for classes creating/refreshing a materialised view
    on Postgres.

    Subclasses must define their own :attr:`table` and
    :attr:`query` properties, and optionally :attr:`columns`.
    """

    table = NotImplementedProperty
    'View to create and refresh'

    query = NotImplementedProperty
    'Query to run'

    columns = None
    'Columns names in created table'

    def run(self):
        query = textwrap.dedent("""
            CREATE MATERIALIZED VIEW IF NOT EXISTS {table}
            AS
            {query}
            WITH NO DATA;

            REFRESH MATERIALIZED VIEW {table};
        """).strip().format(
            table=self.table,
            query=self.query.strip().rstrip(';'),
        )

        connection = self.output().connect()
        cursor = connection.cursor()
        cursor.execute(query)

        # Mark task as complete in table_updates table in same transaction
        self.output().touch()

        # Clean up
        connection.commit()
        connection.close()

    def output(self):
        return targets.PostgresTableTarget(
            table=self.table,
            columns=self.columns,
            update_id=self.task_id,
            **utils.parse_pg_url(settings.DATABASE_URL)
        )


class SlackReportBase(
        TaskBase,
        mixins.SlackClientMixin,
        ):

    """
    Base class for classes outputting their results to Slack.
    """

    def output(self):
        return luigi.postgres.PostgresTarget(
            update_id=self.task_id,
            table=None,
            **utils.parse_pg_url(settings.DATABASE_URL)
        )


class QueryToSlackReportBase(
        SlackReportBase,
        mixins.PostgresClientMixin,
        ):

    """
    Base class for classes outputting the results of a Postgres
    query to Slack.
    """

    query = NotImplementedProperty
    'Query to run on Postgres'

    transform = lambda x: x
    'Any transforms to do to the dataset'

    slack_channel = '#darts'

    def run(self):
        results = self.postgres_client.query(self.query)

        dataset = self.transform(results.dataset)

        table_output = textwrap.dedent("""
            ```
            {}
            ```
        """).strip().format(dataset)

        csv_filename = 'output/' + self.task_id + '.csv'
        with open(csv_filename, 'w') as out:
            out.write(dataset.csv)

        self.slack_client.chat.post_message(
            channel=self.slack_channel,
            username=settings.SLACK_BOT_NAME,
            text=table_output,
        )
        self.slack_client.files.upload(
            csv_filename,
            channels=self.slack_channel,
            filetype='csv',
            filename=csv_filename,
        )

        self.output().touch()

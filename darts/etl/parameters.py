import arrow
import luigi


class WeekParameter(luigi.Parameter):

    """
    Enables dates passed on the command line to be floored
    to the week (Sunday-Sunday).

    Expects dates in ISO-8601 (YYYY-MM-DD) format.
    """

    def serialise(self, dt):
        return str(dt)

    def parse(self, dt):
        return arrow.get(dt).floor('week').date()

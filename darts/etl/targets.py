import luigi


class PostgresTableTarget(luigi.postgres.PostgresTarget):

    def __init__(self, table, columns=None, *args, **kwargs):
        self.table = table
        self.columns = columns
        super(PostgresTableTarget, self).__init__(table=table, *args, **kwargs)

    def rows(self):
        connection = self.connect()
        with connection.cursor() as cursor:
            cursor.execute('SELECT * FROM {}'.format(self.table))
            for row in cursor:
                yield row
        connection.close()

    def dictrows(self):
        if self.columns is None:
            raise ValueError('Column names required in order to make dicts')
        for row in self.rows():
            yield dict(zip(self.columns, row))

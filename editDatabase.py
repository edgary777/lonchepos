import sqlite3

class Db(object):
    """Database communication class."""

    def __init__(self):
        """Init."""
        self.database = "database.db"

        self.initializer()

    def initializer(self):
            """If table not exists create it."""
            connection = sqlite3.connect(self.database)
            cursor = connection.cursor()

            query = """ALTER TABLE appTickets ADD cashOrder INT;"""
            cursor.execute(query)


doThing = Db()
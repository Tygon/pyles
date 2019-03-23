import sqlite3
import abc

class Database():
    @abc.abstractmethod
    def eq_exists(self, eq_string):
        raise NotImplementedError()

    @abc.abstractmethod
    def add_eq(self, eq_string):
        raise NotImplementedError()

    @abc.abstractmethod
    def get_test_count(self):
        raise NotImplementedError()

class SqliteDatabase(Database):
    def __init__(self):
        self.conn = sqlite3.connect(':memory:')
        self.c = self.conn.cursor()

        self.c.execute('''CREATE TABLE tested_eqs (eq_string)''')

        self.conn.commit()

    def eq_exists(self, eq_string):
        self.c.execute("SELECT eq_string FROM tested_eqs WHERE eq_string=?", (eq_string,))
        return self.c.rowcount > 0

    def add_eq(self, eq_string):
        self.c.execute("INSERT INTO tested_eqs VALUES (?)", (eq_string,))
        self.conn.commit()

    def get_test_count(self):
        self.c.execute("SELECT 1 FROM tested_eqs")
        return self.c.rowcount

class SetDatabase(Database):
    def __init__(self):
        self.tested_eqs = set()

    def eq_exists(self, eq_string):
        return eq_string in self.tested_eqs

    def add_eq(self, eq_string):
        self.tested_eqs.add(eq_string)

    def get_test_count(self):
        return len(self.tested_eqs)
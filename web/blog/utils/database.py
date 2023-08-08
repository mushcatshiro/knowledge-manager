import os
import psycopg2 as p
from psycopg2.extras import RealDictCursor
import sqlite3 as s


class BaseConx:
    def __init__(self, dsn, query_string, dbopt, format_string=None):
        self.dsn = dsn
        self.query_string:str =\
            self.format_query_string(query_string, format_string)
        self.dbopt = dbopt

    def format_query_string(self, query_string, format_string):
        if format_string:
            query_string = self._format_query_string(
                query_string,
                format_string
            )
        return query_string.replace("\n", " ").replace("    ", "")

    def _format_query_string(self, query_string, format_string):
        pass

    def establish_conx(self):
        raise NotImplementedError

    def run(self):
        print(self.query_string)
        ret = None
        error = False
        try:
            conn = self.establish_conx()
            cur = conn.cursor()
            cur.execute(self.query_string)
            if self.dbopt == "QUERY":
                ret = cur.fetchall()
        except Exception as e:
            print(e)
            conn.rollback()
            error = True
        else:
            conn.commit()
        finally:
            conn.close()
        return ret, error

class Sqlite3Conx(BaseConx):
    def __init__(self, dsn, query_string, dbopt, format_string):
        super().__init__(dsn, query_string, dbopt, format_string)
    
    def establish_conx(self):
        if not os.path.isabs(self.dsn):
            raise Exception(
                f"invalid absolute path {self.dsn}"
            )
        return s.connect(self.dsn)

class PostgresConx(BaseConx):
    def __init__(self, dsn, query_string, dbopt, format_string):
        super().__init__(dsn, query_string, dbopt, format_string)
    
    def establish_conx(self):
        return p.connect(
            self.dsn,
            cursor_factory=RealDictCursor
        )


def initialize_cloud(dsn):
    p = PostgresConx(
        dsn,
        '''
        CREATE TABLE IF NOT EXISTS history (
            id SERIAL PRIMARY KEY,
            page_title TEXT NOT NULL,
            url TEXT NOT NULL,
            description TEXT,
            img TEXT,
            date TEXT NOT NULL,
            is_pushed INT
        ) 
        ''',
        'INSERT'
    )
    p.run()

def push(abspath, dsn):
    s = Sqlite3Conx(
        abspath,
        '''
        SELECT
            page_title, url, desc,
            img, date, 1
        FROM history
        WHERE is_pushed = 0
        ''',
        "QUERY",
        None
    )
    ret, error = s.run()

    if ret:
        format_string = ""
        for i in ret:
            format_string +=\
                "{item},".format(item=i)
        p = PostgresConx(
            dsn,
            '''
            INSERT INTO history (
                page_title, url, description,
                img, date, is_pushed
            )
            VALUES
                {values}
            ''',
            'INSERT',
            format_string
        )
        _, error = p.run()
        if not error:
            page_titles = tuple([
                x[0] for x in ret
            ])
            s = Sqlite3Conx(
                abspath,
                '''
                UPDATE history 
                SET is_pushed = 1
                WHERE page_title IN {page_title}
                ''',
                "UPDATE",
                page_titles
            )
            s.run()   
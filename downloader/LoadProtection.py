import sqlite3
import datetime

import logging
logger = logging.getLogger()


class LoadProtection:

    db_file_name = 'load_protection.db'

    def get_con(self):
        return sqlite3.connect(self.db_path+'/'+self.db_file_name)

    def __init__(self, db_path, max_downloads_per_day):
        self.db_path = db_path
        self.max_downloads_per_day = int(max_downloads_per_day)

    def setup_database_schema(self):
        with self.get_con() as con:
            c = con.cursor()
            sql = 'create table if not exists ' + 'ATTEMPTS' \
                  + ' (id INTEGER PRIMARY KEY AUTOINCREMENT, event_timestamp timestamp)'
            c.execute(sql)
            con.commit()

    def register_new_usage(self):
        with self.get_con() as con:
            now = datetime.datetime.now()
            c = con.cursor()
            sql = 'insert INTO  ' + 'ATTEMPTS(event_timestamp)' + ' values(?)'
            c.execute(sql, [now])
            con.commit()

    def is_allowed_to_handle(self):
        return self.get_attempts_count() > 0

    def get_attempts_count(self):
        with self.get_con() as con:
            c = con.cursor()
            from_date = datetime.datetime.now() - datetime.timedelta(days=1)
            sql = 'select count(distinct(id)) from ' + 'ATTEMPTS' + ' where event_timestamp >= ?'
            c.execute(sql, [from_date])
            result = c.fetchone()
            return max(0, self.max_downloads_per_day - result[0])

    def reset_license(self):
        with self.get_con() as con:
            c = con.cursor()
            sql = 'DELETE FROM ' + 'ATTEMPTS'
            c.execute(sql)
            sql = 'VACUUM'
            c.execute(sql)
            con.commit()

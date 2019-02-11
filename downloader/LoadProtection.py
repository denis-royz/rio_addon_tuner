import sqlite3
import datetime


class LoadProtection:

    max_attempts_per_day = 10

    def get_con(self):
        return sqlite3.connect(self.data_dir+'/'+'load_protection.db')

    def __init__(self, data_dir):
        self.data_dir = data_dir
        with self.get_con() as con:
            con = sqlite3.connect(data_dir+'/'+'load_protection.db')
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
            return max(0, self.max_attempts_per_day - result[0])

    def reset_license(self):
        with self.get_con() as con:
            c = con.cursor()
            sql = 'DELETE FROM ' + 'ATTEMPTS'
            c.execute(sql)
            sql = 'VACUUM'
            c.execute(sql)
            con.commit()

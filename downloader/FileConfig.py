import os
import datetime
import logging
logger = logging.getLogger()


class FileConfig:

    processed_file_name = 'processed.zip'
    raw_file_name = 'latest.zip'
    db_file_name = 'load_protection.db'

    def __init__(self, data_dir):
        self.data_dir = data_dir

    def get_file_with_name(self, name):
        return self.data_dir+'/'+name

    def get_raw_file_path(self):
        return self.raw_file_name

    def get_new_raw_file_path(self):
        return self.get_file_with_name('raw_{date:%H:%M:%S}.zip'.format(date=datetime.datetime.now()))

    def register_raw_file_path(self, path):
        logger.info('Registered new RAW file: {}'.format(path))
        self.raw_file_name = path

    def get_processed_file_path(self):
        return self.get_file_with_name(self.processed_file_name)

    def get_db_file_path(self):
        return self.get_file_with_name(self.db_file_name)

    @staticmethod
    def file_age(file_path):
        exists = os.path.exists(file_path)
        if exists:
            stat = os.stat(file_path)
            return float(stat.st_ctime)
        else:
            return float(0)

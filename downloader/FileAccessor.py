import os
import datetime
import logging
logger = logging.getLogger('FileAccessor')


class FileAccessor:

    prefix = 'raw'
    postfix = 'zip'
    file_path = 'none'

    def __init__(self, data_dir, prefix, postfix):
        self.data_dir = data_dir
        self.prefix = prefix
        self.postfix = postfix

    def get_file_with_name(self, name):
        return self.data_dir+'/'+name

    def get_file_path(self):
        return self.file_path

    def get_new_file_path(self):
        file_name = '{prefix}_{date:%H%M%S}.{postfix}'.format(prefix=self.prefix,
                                                              date=datetime.datetime.now(),
                                                              postfix=self.postfix)
        logger.info('Allocated new file name: {}'.format(file_name))
        return self.get_file_with_name(file_name)

    def register_new_file_path(self, path):
        logger.info('Registered new {} file: {}'.format(self.prefix, path))
        self.file_path = path

    def get_edge(self):
        file_path = self.file_path
        exists = os.path.exists(file_path)
        if exists:
            stat = os.stat(file_path)
            return float(stat.st_ctime)
        else:
            return float(0)

import zipfile
import logging
from threading import Lock
logger = logging.getLogger()


class RioZipTuner:

    lock = Lock()

    def __init__(self, raw_file_accessor, patched_file_accessor):
        self.raw_file_accessor = raw_file_accessor
        self.patched_file_accessor = patched_file_accessor

    def check_source_version(self):
        return self.raw_file_accessor.get_edge()

    def check_dest_version(self):
        return self.patched_file_accessor.get_edge()

    def check_have_latest_version(self):
        source_version = self.check_source_version()
        dest_version = self.check_dest_version()
        return 0 < source_version < dest_version

    def tune(self):
        with self.lock:
            if self.check_source_version() == 0.0:
                logger.info("input file does not exist")
                return
            if self.check_have_latest_version():
                logger.info('Latest version is already tuned')
                return
            source_file_path = self.raw_file_accessor.get_file_path()
            dest_file_path = self.patched_file_accessor.get_new_file_path()
            zin = zipfile.ZipFile(source_file_path, 'r')
            zout = zipfile.ZipFile(dest_file_path, 'w')
            for item in zin.infolist():
                buffer = zin.read(item.filename)
                allowed_to_write_file = True
                if '_kr_' in item.filename.lower():
                    allowed_to_write_file = False
                if '_us_' in item.filename.lower():
                    allowed_to_write_file = False
                if '_tw_' in item.filename.lower():
                    allowed_to_write_file = False
                if '_horde_' in item.filename.lower():
                    allowed_to_write_file = False
                if "RaiderIO/locale/ruRU.lua" in item.filename:
                    allowed_to_write_file = False
                if "RaiderIO/locale/enUS.lua" in item.filename:
                    item.filename = item.filename.replace("enUS.lua", 'ruRU.lua')
                if allowed_to_write_file:
                    zout.writestr(item, buffer)
            zout.close()
            zin.close()
            self.patched_file_accessor.register_new_file_path(dest_file_path)

import zipfile


class RioZipTuner:

    def __init__(self, file_config):
        self.file_config = file_config

    def check_source_version(self):
        return self.file_config.file_age(self.file_config.get_raw_file_path())

    def check_dest_version(self):
        return self.file_config.file_age(self.file_config.get_processed_file_path())

    def check_have_latest_version(self):
        source_version = self.check_source_version()
        dest_version = self.check_dest_version()
        return dest_version is not 0.0 or dest_version > source_version

    def tune(self):
        if self.check_source_version is 0.0:
            print("input file does not exist")
            return
        if not self.check_have_latest_version():
            print('Latest version is already tuned')
            return
        source_file_path = self.file_config.get_raw_file_path()
        dest_file_path = self.file_config.get_processed_file_path()
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

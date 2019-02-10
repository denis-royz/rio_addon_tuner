import os
import zipfile


class RioZipTuner:

    dest_file_name = 'processed.zip'
    source_file_name = 'latest.zip'

    def __init__(self, data_dir):
        self.data_dir = data_dir

    def tune(self):
        source_file_path = self.data_dir + "/" + self.source_file_name
        dest_file_path = self.data_dir + "/" + self.dest_file_name
        exists = os.path.exists(source_file_path)
        if not exists:
            print("input file dies not exist")
            return
        zin = zipfile.ZipFile(source_file_path, 'r')
        zout = zipfile.ZipFile(dest_file_path, 'w', zipfile.ZIP_STORED)
        for item in zin.infolist():
            buffer = zin.read(item.filename)
            allowed_to_write_file = "EU" in item.filename or "RaiderIO/" in item.filename
            if allowed_to_write_file and "RaiderIO/locale" in item.filename:
                if "enUS.lua" in item.filename:
                    item.filename = item.filename.replace("enUS.lua", 'ruRU.lua')
                else:
                    allowed_to_write_file = False
            if allowed_to_write_file:
                zout.writestr(item, buffer)
        zout.close()
        zin.close()


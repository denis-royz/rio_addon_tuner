import urllib.request
from bs4 import BeautifulSoup
from threading import Lock

import logging
logger = logging.getLogger()


class RioClientDownloader:
    url = 'https://www.curseforge.com/wow/addons/raiderio/download/2741639/file'
    curseforge = 'https://wow.curseforge.com/projects/raiderio?gameCategorySlug=addons&projectID=279257'
    lock = Lock()

    def __init__(self, file_accessor):
        self.file_accessor = file_accessor
        opener = urllib.request.build_opener()
        opener.addheaders = [('User-agent', 'Mozilla/5.0')]
        urllib.request.install_opener(opener)

    def check_have_latest_version(self):
        downloaded_version_timestamp = self.check_downloaded_version()
        curse_version_timestamp = self.check_curse_version()
        return 0 < curse_version_timestamp < downloaded_version_timestamp

    def check_downloaded_version(self):
        return self.file_accessor.get_edge()

    def download_latest(self):
        with self.lock:
            if self.check_have_latest_version():
                logger.info('Already have latest version')
                return False
            else:
                logger.info('Downloading new version from curse')
                file_path = self.file_accessor.get_new_file_path()
                urllib.request.urlretrieve(self.url, file_path)
                self.file_accessor.register_new_file_path(file_path)
                logger.info('Downloaded new version from curse')
                return True

    def check_curse_version(self):
        req = urllib.request.Request(self.curseforge)
        f = urllib.request.urlopen(req)
        html = f.read().decode('utf-8')
        soup = BeautifulSoup(html, 'html.parser')
        lrf_info_labels = soup.findAll("span", text='Updated')
        if len(lrf_info_labels) == 1:
            addbr = lrf_info_labels[0].parent.findAll("abbr")[0]
            return float(addbr.attrs['data-epoch'])

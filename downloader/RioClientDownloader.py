import urllib.request
from bs4 import BeautifulSoup
from threading import Lock


class RioClientDownloader:

    url = 'https://wow.curseforge.com/projects/raiderio/files/latest'
    curseforge = 'https://wow.curseforge.com/projects/raiderio?gameCategorySlug=addons&projectID=279257'

    def __init__(self, file_config):
        self.file_config = file_config
        opener = urllib.request.build_opener()
        opener.addheaders = [('User-agent', 'Mozilla/5.0')]
        urllib.request.install_opener(opener)

    def check_have_latest_version(self):
        downloaded_version_timestamp = self.check_downloaded_version()
        curse_version_timestamp = self.check_curse_version()
        return curse_version_timestamp > downloaded_version_timestamp

    def check_downloaded_version(self):
        return self.file_config.file_age(self.file_config.get_raw_file_path())

    def download_latest(self):
        lock = Lock()
        with lock:
            if self.check_have_latest_version():
                file_path = self.file_config.get_new_raw_file_path()
                print('Downloading new version from curse')
                urllib.request.urlretrieve(self.url, file_path)
                self.file_config.register_raw_file_path(file_path)
                return True
            else:
                print('Already have latest version')
                return False

    def check_curse_version(self):
        req = urllib.request.Request(self.curseforge)
        f = urllib.request.urlopen(req)
        html = f.read().decode('utf-8')
        soup = BeautifulSoup(html, 'html.parser')
        lrf_info_labels = soup.findAll("div", {"class": "info-label"}, text='Last Released File')
        if len(lrf_info_labels) == 1:
            addbr = lrf_info_labels[0].parent.findAll("abbr")[0]
            return float(addbr.attrs['data-epoch'])

import urllib.request
import os
from bs4 import BeautifulSoup


class RioClientDownloader:

    url = 'https://wow.curseforge.com/projects/raiderio/files/latest'
    curseforge = 'https://wow.curseforge.com/projects/raiderio?gameCategorySlug=addons&projectID=279257'
    dest_file_name = 'latest.zip'

    def __init__(self, data_dir):
        self.data_dir = data_dir
        opener = urllib.request.build_opener()
        opener.addheaders = [('User-agent', 'Mozilla/5.0')]
        urllib.request.install_opener(opener)

    def download_latest(self):
        downloaded_version_timestamp = self.check_downloaded_version()
        curse_version_timestamp = self.check_curse_version()
        if curse_version_timestamp > downloaded_version_timestamp:
            print('Downloading new version from curse')
            file_path = self.data_dir + "/" + self.dest_file_name
            urllib.request.urlretrieve(self.url, file_path)
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

    def check_downloaded_version(self):
        file_path = self.data_dir + "/" + self.dest_file_name
        exists = os.path.exists(file_path)
        if exists:
            stat = os.stat(file_path)
            return float(stat.st_ctime)
        else:
            return float(0)

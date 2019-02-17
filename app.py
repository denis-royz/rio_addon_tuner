from flask import Flask, render_template, send_file, abort
from envparse import Env
from downloader.RioClientDownloader import RioClientDownloader
from downloader.RioZipTuner import RioZipTuner
from downloader.LoadProtection import LoadProtection
from downloader.PersonalRecommendation import PersonalRecommendation
from downloader.FileAccessor import FileAccessor
from datetime import datetime
import logging
import sys


app = Flask(__name__)
env = Env(
    HOST=dict(cast=str,  default='0.0.0.0'),
    HTTP_PORT=dict(cast=int,  default='5000'),
    DATA_DIR=dict(cast=str,  default='../data'),
    DOWNLOADS_PER_DAY=dict(cast=int,  default='10')
)
env.read_envfile()
raw_file_accessor = FileAccessor(env.str('DATA_DIR'), 'raw', 'zip')
patched_file_accessor = FileAccessor(env.str('DATA_DIR'), 'patched', 'zip')
rio_downloader = RioClientDownloader(raw_file_accessor)
rio_tuner = RioZipTuner(raw_file_accessor, patched_file_accessor)
load_protection = LoadProtection(env.str('DATA_DIR'), max_downloads_per_day=env.int('DOWNLOADS_PER_DAY'))
load_protection.setup_database_schema()
personalRecommendation = PersonalRecommendation()

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s-%(name)s-%(levelname)s: %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)


def format_date(date_long, message_in_case_date_is_zero):
    if date_long > 0.0:
        return datetime.fromtimestamp(date_long)
    else:
        return message_in_case_date_is_zero


def get_model():
    tuned_version_unix_time = rio_tuner.check_dest_version()
    raw_version_unix_time = rio_tuner.check_source_version()
    allowed_downloads = load_protection.get_attempts_count()
    wow_path = personalRecommendation.get_path_to_wow()
    model = dict(
        latest_tuned_version_date=format_date(tuned_version_unix_time, 'No tuned zip presented'),
        latest_raw_version_date=format_date(raw_version_unix_time, 'No RIO zip presented'),
        allowed_downloads=allowed_downloads,
        wow_path=wow_path
    )
    return model


@app.route('/')
def root():
    return render_template('index.html', model=get_model())


@app.route('/download_latest')
def download_latest():
    rio_downloader.download_latest()
    return render_template('index.html', model=get_model())


@app.route('/raider_io_tuned')
def download():
    rio_downloader.download_latest()
    rio_tuner.tune()
    if load_protection.is_allowed_to_handle():
        load_protection.register_new_usage()
        return send_file(patched_file_accessor.get_file_path(), cache_timeout=-1)
    else:
        abort(403)


@app.route('/raider_io_raw')
def download_raw():
    rio_downloader.download_latest()
    if load_protection.is_allowed_to_handle():
        load_protection.register_new_usage()
        return send_file(raw_file_accessor.get_file_path(), cache_timeout=-1)
    else:
        abort(403)


@app.errorhandler(404)
def page_not_found(e):
    # note that we set the 404 status explicitly
    return render_template('404.html'), 404


if __name__ == '__main__':
    print('HOST =', env.str('HOST'))
    print('HTTP_PORT =', env.int('HTTP_PORT'))
    print('DATA_DIR =', env.str('DATA_DIR'))
    app.run(host=env.str('HOST'), port=env.int('HTTP_PORT'))

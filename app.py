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
import os
import schedule
import time
import threading

app = Flask(__name__)
env = Env(
    HOST=dict(cast=str,  default='0.0.0.0'),
    HTTP_PORT=dict(cast=int,  default='5000'),
    DATA_DIR=dict(cast=str,  default='data'),
    DOWNLOADS_PER_DAY=dict(cast=int,  default='10')
)
env.read_envfile()

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s-%(name)s-%(levelname)s: %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

raw_file_accessor = FileAccessor(env.str('DATA_DIR'), 'raw', 'zip')
patched_file_accessor = FileAccessor(env.str('DATA_DIR'), 'patched', 'zip')
load_protection = LoadProtection(env.str('DATA_DIR'), max_downloads_per_day=env.int('DOWNLOADS_PER_DAY'))
rio_downloader = RioClientDownloader(raw_file_accessor)
rio_tuner = RioZipTuner(raw_file_accessor, patched_file_accessor)
personalRecommendation = PersonalRecommendation()

running = True
enabled_scheduler = True


def format_date(date_long, message_in_case_date_is_zero):
    if date_long > 0.0:
        return datetime.fromtimestamp(date_long)
    else:
        return message_in_case_date_is_zero


def get_model():
    tuned_version_unix_time = rio_tuner.check_dest_version()
    raw_version_unix_time = rio_tuner.check_source_version()
    allowed_downloads = load_protection.get_attempts_count()
    personal_recommendation = personalRecommendation.get_personal_recommendation()
    personal_recommendation_title = personalRecommendation.get_personal_recommendation_title()
    model = dict(
        latest_tuned_version_date=format_date(tuned_version_unix_time, 'No tuned zip presented'),
        latest_raw_version_date=format_date(raw_version_unix_time, 'No RIO zip presented'),
        allowed_downloads=allowed_downloads,
        personal_recommendation=personal_recommendation,
        personal_recommendation_title=personal_recommendation_title
    )
    return model


def schedule_nightly_tasks():
    logger.info("schedule_nightly_tasks")
    schedule.every().day.at("04:30").do(scheduled).tag('daily-tasks')
    while running and enabled_scheduler:
        schedule.run_pending()
        time.sleep(1)


def scheduled():
    rio_downloader.download_latest()
    rio_tuner.tune()


@app.route('/')
def root():
    return render_template('index.html', model=get_model())


@app.route('/raider_io_tuned')
def download():
    if load_protection.is_allowed_to_handle():
        rio_downloader.download_latest()
        rio_tuner.tune()
        load_protection.register_new_usage()
        return send_file(patched_file_accessor.get_file_path(), cache_timeout=-1)
    else:
        abort(403)


@app.route('/raider_io_raw')
def download_raw():
    if load_protection.is_allowed_to_handle():
        rio_downloader.download_latest()
        load_protection.register_new_usage()
        return send_file(raw_file_accessor.get_file_path(), cache_timeout=-1)
    else:
        abort(403)


@app.errorhandler(404)
def page_not_found(e):
    # note that we set the 404 status explicitly
    return render_template('404.html'), 404


if __name__ == '__main__':
    if not os.path.isdir(env.str('DATA_DIR')):
        os.mkdir(env.str('DATA_DIR'))
    load_protection.setup_database_schema()
    threading.Thread(target=schedule_nightly_tasks).start()
    app.run(host=env.str('HOST'), port=env.int('HTTP_PORT'))
    running = False

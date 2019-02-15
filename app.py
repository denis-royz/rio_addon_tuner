from flask import Flask, render_template, send_file
from envparse import Env
from downloader.RioClientDownloader import RioClientDownloader
from downloader.RioZipTuner import RioZipTuner
from downloader.LoadProtection import LoadProtection
from downloader.PersonalRecommendation import PersonalRecommendation
from downloader.FileConfig import FileConfig
from datetime import datetime


app = Flask(__name__)
env = Env(
    HOST=dict(cast=str,  default='0.0.0.0'),
    HTTP_PORT=dict(cast=int,  default='5000'),
    DATA_DIR=dict(cast=str,  default='../data'),
    DOWNLOADS_PER_DAY=dict(cast=int,  default='10')
)
env.read_envfile()
file_config = FileConfig(data_dir=env.str('DATA_DIR'))
rio_downloader = RioClientDownloader(file_config)
rio_tuner = RioZipTuner(file_config)
load_protection = LoadProtection(file_config, max_downloads_per_day=env.int('DOWNLOADS_PER_DAY'))
load_protection.setup_database_schema()
personalRecommendation = PersonalRecommendation()


def format_date(date_long, message_in_case_date_is_zero):
    if date_long > 0.0:
        return datetime.fromtimestamp(date_long)
    else:
        return message_in_case_date_is_zero


def get_model():
    tuned_version_unix_time = load_protection.protected_call(rio_tuner.check_dest_version)
    raw_version_unix_time = load_protection.protected_call(rio_tuner.check_source_version)
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
    load_protection.protected_call(rio_tuner.tune)
    if load_protection.is_allowed_to_handle():
        load_protection.register_new_usage()
        return send_file('data/processed.zip', attachment_filename='raider_io_tuned.zip')
    else:
        raise Exception


@app.route('/raider_io_raw')
def download_raw():
    rio_downloader.download_latest()
    if load_protection.is_allowed_to_handle():
        load_protection.register_new_usage()
        return send_file(file_config.get_raw_file_path(), attachment_filename='raider_io_raw.zip')
    else:
        raise Exception


if __name__ == '__main__':
    print('HOST =', env.str('HOST'))
    print('HTTP_PORT =', env.int('HTTP_PORT'))
    print('DATA_DIR =', env.str('DATA_DIR'))
    app.run(host=env.str('HOST'), port=env.int('HTTP_PORT'))

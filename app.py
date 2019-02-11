from flask import Flask, render_template, send_file
from envparse import Env
from downloader.RioClientDownloader import RioClientDownloader
from downloader.RioZipTuner import RioZipTuner
from datetime import datetime

app = Flask(__name__)
env = Env(
    HOST=dict(cast=str,  default='0.0.0.0'),
    HTTP_PORT=dict(cast=int,  default='5000'),
    DATA_DIR=dict(cast=int,  default='../data')
)
env.read_envfile()
rio_downloader = RioClientDownloader(data_dir=env.str('DATA_DIR'))
rio_tuner = RioZipTuner(data_dir=env.str('DATA_DIR'))


def format_date(date_long, message_in_case_date_is_zero):
    if date_long > 0.0:
        return datetime.fromtimestamp(date_long)
    else:
        return message_in_case_date_is_zero


def get_model():
    tuned_version_unix_time = rio_tuner.check_dest_version()
    raw_version_unix_time = rio_tuner.check_source_version()
    model = dict(
        latest_tuned_version_date=format_date(tuned_version_unix_time, 'No tuned zip presented'),
        latest_raw_version_date=format_date(raw_version_unix_time, 'No RIO zip presented')
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
    return send_file('data/processed.zip', attachment_filename='raider_io_tuned.zip')


@app.route('/raider_io_raw')
def download_raw():
    rio_downloader.download_latest()
    return send_file('data/latest.zip', attachment_filename='raider_io_raw.zip')


if __name__ == '__main__':
    print('HOST =', env.str('HOST'))
    print('HTTP_PORT =', env.int('HTTP_PORT'))
    print('DATA_DIR =', env.str('DATA_DIR'))
    app.run(host=env.str('HOST'), port=env.int('HTTP_PORT'))

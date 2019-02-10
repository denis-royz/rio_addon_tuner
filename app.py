from flask import Flask, render_template
from envparse import Env
from downloader.RioClientDownloader import RioClientDownloader
from downloader.RioZipTuner import RioZipTuner

app = Flask(__name__)
env = Env(
    HOST=dict(cast=str,  default='0.0.0.0'),
    HTTP_PORT=dict(cast=int,  default='5000'),
    DATA_DIR=dict(cast=int,  default='../data')
)
env.read_envfile()
rio_downloader = RioClientDownloader(data_dir=env.str('DATA_DIR'))
rio_tuner = RioZipTuner(data_dir=env.str('DATA_DIR'))


@app.route('/')
def root():
    return render_template('index.html')


@app.route('/download_latest')
def download_latest():
    rio_downloader.download_latest()
    return render_template('index.html')


if __name__ == '__main__':
    print('HOST =', env.str('HOST'))
    print('HTTP_PORT =', env.int('HTTP_PORT'))
    print('DATA_DIR =', env.str('DATA_DIR'))
    app.run(host=env.str('HOST'), port=env.int('HTTP_PORT'))

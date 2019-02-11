
from envparse import Env
from downloader.LoadProtection import LoadProtection

env = Env(
    HOST=dict(cast=str,  default='0.0.0.0'),
    HTTP_PORT=dict(cast=int,  default='5000'),
    DATA_DIR=dict(cast=int,  default='data')
)
env.read_envfile()


if __name__ == '__main__':
    lp = LoadProtection(data_dir=env.str('DATA_DIR'))
    print(lp.get_attempts_count())
    print(lp.register_new_usage())
    print(lp.get_attempts_count())

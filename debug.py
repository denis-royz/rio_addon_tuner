
from envparse import Env

env = Env(
    HOST=dict(cast=str,  default='0.0.0.0'),
    HTTP_PORT=dict(cast=int,  default='5000'),
    DATA_DIR=dict(cast=int,  default='data')
)
env.read_envfile()


if __name__ == '__main__':
    print("null")

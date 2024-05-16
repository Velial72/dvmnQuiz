import redis
from environs import Env


env = Env()
env.read_env()
# Создание подключения к Redis
redis_client = redis.StrictRedis(
    host=env('REDIS_HOST'),
    port=env('REDIS_PORT'),
    password=env('REDIS_PASSWORD'),
    decode_responses=True
)
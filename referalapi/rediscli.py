import redis
from decouple import config

redis_client = redis.Redis(host=config('REDIS_HOST'), port=config('REDIS_PORT', cast=int), db=0)

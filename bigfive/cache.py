from flask_cache import Cache
import redis
from bigfive.config import REDIS_HOST,REDIS_PORT
try:
    rds = redis.Redis(host=REDIS_HOST,port=REDIS_PORT)
    rds.ping()
    cache = Cache(config={'CACHE_TYPE': 'redis','CACHE_REDIS_URL':'redis://{REDIS_HOST}:{REDIS_PORT}'.format(REDIS_HOST=REDIS_HOST,REDIS_PORT=REDIS_PORT)})
except:
    cache = Cache(config={'CACHE_TYPE': 'simple'})
print(cache.config)

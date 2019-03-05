from flask_cache import Cache
cache = Cache(config={'CACHE_TYPE': 'simple'})
# cache = Cache(config={'CACHE_TYPE': 'redis','CACHE_REDIS_URL':'redis://219.224.134.226:10010'})


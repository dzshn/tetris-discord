import aioredis
import fakeredis.aioredis
import redis

from bot import config


def get_object() -> aioredis.Redis:
    lib = config.data['redis']
    if lib == 'aioredis':
        return aioredis.from_url('redis://localhost')

    elif lib == 'fakeredis':
        return fakeredis.aioredis.FakeRedis()

    else:
        try:
            redis.from_url('redis://localhost').ping()

        except redis.ConnectionError:
            return fakeredis.aioredis.FakeRedis()

        else:
            return aioredis.from_url('redis://localhost')

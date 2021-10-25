import aioredis
import fakeredis.aioredis
import redis

db_ids = {
    'settings': 0,
    'zen': 1,
    'marathon': 2,
}


def get_session(name: str) -> aioredis.Redis:
    try:
        redis.from_url('redis://localhost').ping()

    except redis.ConnectionError:
        return fakeredis.aioredis.FakeRedis(db=db_ids[name])

    return aioredis.from_url('redis://localhost', db=db_ids[name])

import aioredis
import fakeredis.aioredis
import redis


def get_session(db_id: int) -> aioredis.Redis:
    try:
        redis.from_url('redis://localhost').ping()

    except redis.ConnectionError:
        return fakeredis.aioredis.FakeRedis(db=db_id)

    return aioredis.from_url('redis://localhost', db=db_id)

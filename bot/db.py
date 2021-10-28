from typing import Union

import aioredis
import fakeredis.aioredis
import redis

db_ids = {
    'settings': 0,
    'zen': 1,
    'marathon': 2,
}


def get_session(name: Union[str, int] = 0) -> aioredis.Redis:
    db_id = db_ids[name] if isinstance(name, str) else name

    try:
        redis.from_url('redis://localhost').ping()

    except redis.ConnectionError:
        return fakeredis.aioredis.FakeRedis(db=db_id)

    return aioredis.from_url('redis://localhost', db=db_id)

from redis.asyncio import Redis

from courageous_comets.settings import Settings

redis = Redis(
    host=Settings.REDIS_HOST,
    port=Settings.REDIS_PORT,
    password=Settings.REDIS_PASSWORD,
)

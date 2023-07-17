import dramatiq
from dramatiq.encoder import JSONEncoder
from dramatiq.brokers.redis import RedisBroker
from dramatiq.results import Results
from dramatiq.results.backends.redis import RedisBackend
import dramatiq.middleware

def setup():
    encoder = JSONEncoder()
    backend = RedisBackend(url="redis://127.0.0.1:6379/1", encoder=encoder)
    broker = RedisBroker(url="redis://127.0.0.1:6379/0")
    broker.add_middleware(Results(backend=backend))
    dramatiq.set_broker(broker)
    dramatiq.set_encoder(encoder)
    
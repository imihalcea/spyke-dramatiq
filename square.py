import dramatiq
from dramatiq.logging import get_logger
from plumbing import setup

setup()
logger = get_logger(__name__)

@dramatiq.actor(store_results=True, max_retries=0, queue_name="square")
def square(x:int) -> int:
    logger.info(f"The square of {x} is {x * x}")
    return x * x
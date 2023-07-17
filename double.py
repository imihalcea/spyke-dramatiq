import dramatiq
from dramatiq.logging import get_logger

logger = get_logger(__name__)

@dramatiq.actor(max_retries=0, queue_name="double")
def double(x:int) -> int:
    logger.info(f"the double of {x} is {x * 2}")
    return x * 2
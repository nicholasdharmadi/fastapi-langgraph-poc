"""RQ worker for processing background tasks."""
import logging
from redis import Redis
from rq import Worker, Queue
from app.config import settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Redis connection
redis_conn = Redis.from_url(settings.REDIS_URL)

if __name__ == '__main__':
    logger.info("Starting RQ worker...")
    
    # RQ 2.0+ doesn't need Connection context manager
    worker = Worker(['campaigns'], connection=redis_conn)
    worker.work()


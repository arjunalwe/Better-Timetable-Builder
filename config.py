from redis import Redis
from rq import Queue
from dotenv import load_dotenv
import os

load_dotenv()
REDIS_URL = os.environ.get("REDIS_URL")

conn = Redis.from_url(REDIS_URL)
ttb_queue = Queue("ttb_queue", connection=conn)
acorn_queue = Queue("acorn_queue", connection=conn)
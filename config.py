from redis import Redis
from rq import Queue
from dotenv import load_dotenv
import os

load_dotenv()
REDIS_URL = os.environ.get("REDIS_URL")

conn = Redis.from_url(REDIS_URL)
course_info_queue = Queue("course_info_queue", connection=conn)
prereqs_queue = Queue("prereqs_queue", connection=conn)
program_queue = Queue("program_queue", connection=conn)

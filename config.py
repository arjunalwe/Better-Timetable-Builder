from redis import Redis
from rq import Queue
from dotenv import load_dotenv
import os

load_dotenv()
REDIS_URL = os.environ.get("REDIS_URL")

conn = Redis.from_url(REDIS_URL, health_check_interval=100)
course_info_queue = Queue("course_info_queue", connection=conn)
prereq_queue = Queue("prereq_queue", connection=conn)
program_queue = Queue("program_queue", connection=conn)
category_queue = Queue("category_queue", connection=conn)
from utils import get_total_pages
from config import ttb_queue
from rq import Queue
from tasks.ttb_task import pull_from_ttb

pages = get_total_pages()

jobs = []
for i in range(1, pages+1):
    jobs.append(Queue.prepare_data(pull_from_ttb, (i,)))

ttb_queue.enqueue_many(jobs)
from datetime import datetime, timezone
import time
from utils import get_total_pages, get_programs
from config import course_info_queue, prereqs_queue, program_queue
from config import conn as redis_conn
from database import get_db_pool
from rq import Queue
from tasks.course_info_task import pull_course_info
from tasks.program_task import pull_programs
from tasks.prereqs_task import pull_prereqs
from constants import MIN_FETCH_INTERVAL

cookie = None
while not cookie:
    cookie = redis_conn.lpop("acorn_cookies")
    if not cookie:
        time.sleep(5)

redis_conn.lpush("acorn_cookies", cookie)

start_time = datetime.now(timezone.utc)

pages = get_total_pages()

course_info_jobs = []
for i in range(1, pages + 1):
    course_info_jobs.append(Queue.prepare_data(pull_course_info, (i, start_time)))

course_info_queue.enqueue_many(course_info_jobs)
course_info_reg = course_info_queue.started_job_registry

while course_info_reg.get_job_count() or len(course_info_queue):
    time.sleep(1)
    

with get_db_pool().connection() as conn:
    with conn.cursor() as cur:
        cur.execute("""
                    SELECT id FROM bronze_course_data 
                    WHERE prereq_json IS NULL 
                    OR updated <= CURRENT_TIMESTAMP - INTERVAL %s;
                    """, (MIN_FETCH_INTERVAL,)) 
        
        courses = cur.fetchall()
                
        cur.execute("""
                    SELECT id FROM bronze_program_data 
                    WHERE json IS NULL 
                    OR updated <= CURRENT_TIMESTAMP - INTERVAL %s;
                    """, (MIN_FETCH_INTERVAL,))
        
        programs_db = [i[0].split("-")[0] for i in cur.fetchall()]
        
programs = get_programs()

program_jobs = [Queue.prepare_data(pull_programs, (program,)) for program in programs if program in programs_db]
prereqs_jobs = [Queue.prepare_data(pull_prereqs, (i[0],)) for i in courses]

prereqs_queue.enqueue_many(prereqs_jobs)
program_queue.enqueue_many(program_jobs)
        
        
prereqs_reg = prereqs_queue.started_job_registry
program_reg = program_queue.started_job_registry

while True:
    time.sleep(1)
    if not any(
        [
            prereqs_reg.get_job_count(),
            program_reg.get_job_count(),
            len(prereqs_queue),
            len(program_queue)
        ]
    ):
        break

with get_db_pool().connection() as conn:
    with conn.cursor() as cur:
        cur.execute(
            """
            UPDATE bronze_course_data SET is_active = FALSE WHERE last_seen < %s;
            UPDATE bronze_program_data SET is_active = FALSE WHERE last_seen < %s;
            """,
            (start_time, start_time),
        )
        
redis_conn.delete("acorn_cookies")

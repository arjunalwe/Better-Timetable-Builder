from datetime import datetime, timezone
import time
from utils import get_total_pages, get_programs
from config import course_info_queue, prereqs_queue, program_queue, redis_conn
from database import get_db_pool
from rq import Queue
from tasks.course_info_task import pull_course_info
from tasks.program_task import pull_programs

while True:
    cookie = redis_conn.blpop("acorn_cookies")
    redis_conn.lpush("acorn_cookies", cookie[1])

    start_time = datetime.now(timezone.utc)

    pages = get_total_pages()
    
    course_info_jobs = []
    for i in range(1, pages + 1):
        course_info_jobs.append(Queue.prepare_data(pull_course_info, (i, start_time)))

    course_info_queue.enqueue_many(course_info_jobs)
    
    programs = get_programs()
    program_jobs = [Queue.prepare_data(pull_programs, (program,)) for program in programs]
    
    program_queue.enqueue_many(program_jobs)

    course_info_reg = course_info_queue.started_job_registry
    prereqs_reg = prereqs_queue.started_job_registry
    program_reg = program_queue.started_job_registry

    while True:
        time.sleep(5)
        if not any(
            [
                course_info_reg.get_job_count(),
                prereqs_reg.get_job_count(),
                program_reg.get_job_count(),
                len(course_info_queue),
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

from datetime import datetime, timezone
import time
from utils import get_total_pages, get_programs, pause_until_queue
from config import course_info_queue, prereq_queue, program_queue, category_queue
from config import conn as redis_conn
from database import get_db_pool
from rq import Queue
from tasks.course_info_task import pull_course_info
from tasks.program_task import pull_programs
from tasks.prereqs_task import pull_prereqs
from tasks.category_task import pull_categories
import re
from constants import MIN_FETCH_INTERVAL

start_time = datetime.now(timezone.utc)

pages = get_total_pages()

try:
    course_info_jobs = []
    for i in range(1, pages + 1):
        course_info_jobs.append(
            Queue.prepare_data(pull_course_info, (i, start_time), job_id=f"course_page_{i}")
        )

    course_info_queue.enqueue_many(course_info_jobs)
    course_info_reg = course_info_queue.started_job_registry

    pause_until_queue(1, course_info_queue)

    cookie = None
    while not cookie:
        cookie = redis_conn.lpop("acorn_cookies")
        if not cookie:
            time.sleep(5)

    redis_conn.lpush("acorn_cookies", cookie)

    with get_db_pool().connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT course_id FROM bronze.course_data 
                WHERE prerequisite_payload IS NULL 
                OR last_seen_at <= CURRENT_TIMESTAMP - CAST(%s as INTERVAL);
                """,
                (MIN_FETCH_INTERVAL,),
            )

            courses = cur.fetchall()

            cur.execute(
                """
                SELECT program_id FROM bronze.program_data 
                WHERE requirement_payload IS NULL 
                OR last_seen_at <= CURRENT_TIMESTAMP - CAST(%s as INTERVAL);
                """,
                (MIN_FETCH_INTERVAL,),
            )

            programs_stale = [i[0].split("-")[0] for i in cur.fetchall()]

            cur.execute("SELECT program_id FROM bronze.program_data;")
            programs_all = [i[0].split("-")[0] for i in cur.fetchall()]

    programs = get_programs()

    program_jobs = [
        Queue.prepare_data(pull_programs, (program,), job_id=f"prog_{program.split('-')[0].strip()}")
        for program in programs
        if (program not in programs_all) or (program in programs_stale)
    ]
    prereqs_jobs = [
        Queue.prepare_data(pull_prereqs, (i[0],), job_id=f"prereq_{i[0]}") for i in courses
    ]

    prereq_queue.enqueue_many(prereqs_jobs)
    program_queue.enqueue_many(program_jobs)

    pause_until_queue(1, prereq_queue, program_queue)
        
    with get_db_pool().connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                        WITH extracted_pointers AS (
                            SELECT DISTINCT 
                                (jsonb_path_query(requirement_payload::jsonb, '$.** ? (@.categoryEntity == true).code'::jsonpath) #>> '{}') AS category_code
                            FROM bronze.program_data
                            WHERE requirement_payload IS NOT NULL
                        )
                        SELECT e.category_code
                        FROM extracted_pointers e
                        LEFT JOIN bronze.category_data c 
                            ON e.category_code = c.category_id
                        WHERE c.category_id IS NULL 
                        OR c.category_payload IS NULL
                        OR c.last_seen_at <= CURRENT_TIMESTAMP - CAST(%s as INTERVAL);
                        """, (MIN_FETCH_INTERVAL,))
            
            categories = cur.fetchall()

    category_jobs = []
    for category in categories:
        job_id = re.sub(r'[^a-zA-Z0-9_-]', '', category[0])
        category_jobs.append(Queue.prepare_data(pull_categories, (category[0],), job_id=job_id))
        
    category_queue.enqueue_many(category_jobs)

    pause_until_queue(1, category_queue)

finally:
    with get_db_pool().connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "UPDATE bronze.course_data SET is_active = FALSE WHERE last_seen_at < %s;",
                (start_time,)
            )
            cur.execute(
                "UPDATE bronze.program_data SET is_active = FALSE WHERE last_seen_at < %s;",
                (start_time,)
            )
            cur.execute(
                "UPDATE bronze.category_data SET is_active = FALSE WHERE last_seen_at < %s;",
                (start_time,)
            )

    redis_conn.delete("acorn_cookies")

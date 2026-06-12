import requests
import utils
from constants import TTB_URL, HEADERS_TTB
from database import get_db_pool
import datetime
from rq import Queue
from tasks.prereqs_task import pull_prereqs
from config import prereqs_queue
import json

def pull_course_info(page: int, start_time: datetime.datetime):
    payload = utils.build_payload()
    payload["page"] = page
    response = requests.post(TTB_URL, json=payload, headers=HEADERS_TTB)
    response.raise_for_status()
    
    jsons = response.json()["payload"]["pageableCourse"]["courses"]
    load = []
    
    for i in jsons:
        id = i["code"] + "-" + ''.join(i["sessions"])
        load.append((id, i["code"], json.dumps(i), "COURSE INFO PULLED"))
        
    if not load:
        return
        
    ids, courses, info_jsons, statuses = zip(*load)
    
    with get_db_pool().connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO bronze_course_data (id, course, info_json, status)
                SELECT * FROM UNNEST(%s, %s, %s, %s)
                ON CONFLICT (id) DO UPDATE 
                SET 
                    info_json = EXCLUDED.info_json,
                    status = EXCLUDED.status,
                    last_seen = CURRENT_TIMESTAMP,
                    updated = CASE 
                        WHEN bronze_course_data.info_json IS DISTINCT FROM EXCLUDED.info_json 
                        THEN CURRENT_TIMESTAMP 
                        ELSE bronze_course_data.updated 
                    END
                RETURNING id, updated
            """, (list(ids), list(courses), list(info_jsons), list(statuses)))
            
            results = cur.fetchall()

    prereq_jobs = []
    for row in results:
        course_id = row[0]
        updated_time = row[1]
        
        if updated_time >= start_time:
            prereq_jobs.append(Queue.prepare_data(pull_prereqs, (course_id,)))
            
    if prereq_jobs:
        prereqs_queue.enqueue_many(prereq_jobs)
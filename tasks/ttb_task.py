import requests
import utils
from constants import TTB_URL, HEADERS_TTB
from database import pool
from rq import Queue
from tasks.acorn_task import pull_from_acorn
from config import acorn_queue
import json

def pull_from_ttb(page: int):
    payload = utils.build_payload()
    payload["page"] = page
    response = requests.post(TTB_URL, json=payload, headers=HEADERS_TTB)
    response.raise_for_status()
    
    jsons = response.json()["payload"]["pageableCourse"]["courses"]
    load = []
    jobs = []
    
    for i in jsons:
        load.append((i["id"], i["code"], json.dumps(i), "TTB COMPLETED"))
        jobs.append(Queue.prepare_data(pull_from_acorn, (i["id"], i["code"])))
    
    with pool.connection() as conn:
        with conn.cursor() as cur:
            
            cur.executemany("""
                        INSERT INTO bronze(id, course, ttb_json, status)
                        VALUES(%s, %s, %s, %s)
                        ON CONFLICT (id) DO UPDATE SET
                            ttb_json = EXCLUDED.ttb_json,
                            updated = CURRENT_TIMESTAMP;
                        """,
                        load
                        )

    acorn_queue.enqueue_many(jobs)
import requests
import utils
from constants import TTB_URL, HEADERS_TTB
from database import get_db_pool
import datetime
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
            unique_records = {}
            for i in range(len(ids)):
                unique_records[ids[i]] = (courses[i], info_jsons[i], statuses[i])

            clean_ids = list(unique_records.keys())
            clean_courses = [val[0] for val in unique_records.values()]
            clean_info_jsons = [val[1] for val in unique_records.values()]
            clean_statuses = [val[2] for val in unique_records.values()]    

            cur.execute("""
                INSERT INTO bronze_course_data (id, course, info_json, status)
                SELECT * FROM UNNEST(%s::text[], %s::text[], %s::jsonb[], %s::text[])
                ON CONFLICT (id) DO UPDATE SET
                    course = EXCLUDED.course,
                    info_json = EXCLUDED.info_json,
                    status = CASE 
                        WHEN bronze_course_data.status = 'PREREQS PULLED' THEN 'PREREQS PULLED'
                        ELSE excluded.status,
                    END
                    last_seen = CURRENT_TIMESTAMP,
                    updated = CASE 
                        WHEN bronze_course_data.info_json IS DISTINCT FROM EXCLUDED.info_json 
                        THEN CURRENT_TIMESTAMP 
                        ELSE bronze_course_data.updated 
                    END
                RETURNING id, updated
            """, (clean_ids, clean_courses, clean_info_jsons, clean_statuses))
            

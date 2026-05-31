import requests
import utils
from constants import TTB_URL, HEADERS_TTB
from database import pool

def pull_from_ttb(page: int):
    payload = utils.build_payload()
    payload["page"] = page
    response = requests.post(TTB_URL, json=payload, headers=HEADERS_TTB)
    response.raise_for_status()
    
    for i in response.json()["payload"]["pageableCourse"]["courses"]:
        
    
    # with pool.connection() as conn:
    #     with conn.cursor() as cur:
            
    #         cur.execute("""
    #                     INSERT INTO bronze(id, course, ttb_json, status, updated)
    #                     VALUES(%s, %s, %s, %s, %s)
                        
    #                     """,
    #                     ()
    #                     )
        

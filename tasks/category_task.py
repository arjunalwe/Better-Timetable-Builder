from database import get_db_pool
from utils import get_dx_headers, get_session, return_cookie
from constants import ACORN_URL
from requests.exceptions import HTTPError
import json

def pull_categories(category: str):
    headers = None
    tab = None
    try:
        tab, headers = get_dx_headers()
        session = get_session()
        session.headers.update(headers)
        
        response = json.dumps(session.get(ACORN_URL[0:-8] + f"Student/getCategoryCourses", params={"categoryCode":category}).json())
        with get_db_pool().connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                            INSERT INTO bronze.category_data(category_id, category_payload, extraction_status)
                            VALUES(%s, %s, %s)
                            ON CONFLICT (category_id) DO UPDATE SET
                                extraction_status = EXCLUDED.extraction_status,
                                category_payload = EXCLUDED.category_payload,
                                is_active = TRUE,
                                last_seen_at = CURRENT_TIMESTAMP,
                                updated_at = CASE 
                                    WHEN bronze.category_data.category_payload IS DISTINCT FROM EXCLUDED.category_payload 
                                    THEN CURRENT_TIMESTAMP 
                                    ELSE bronze.category_data.updated_at 
                                END 
                            """, (category, response, 'CATEGORY PULLED'))
                
    except HTTPError as error:
            print(f"\n{'='*50}", flush=True)
            print(f"FATAL API ERROR ON CATEGORY: {category}", flush=True)
            if error.response is not None:
                print(error.response.text, flush=True)
            print(f"{'='*50}\n", flush=True)
            raise error
        
    finally:
        if headers is not None:
            return_cookie(headers, tab)
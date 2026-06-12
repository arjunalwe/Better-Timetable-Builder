import requests
from utils import get_dx_headers, get_session, return_cookie
import os
import json
from constants import ACORN_URL, CATALOG_YEAR
from database import get_db_pool

def pull_programs(program: str):
    try:
        session = get_session()
        tab, headers = get_dx_headers()
        session.headers.update(headers)

        program_code = program.split("-")[0]

        response = session.post(
            ACORN_URL + f"/saveProgramEntry?tabIndex={tab}&newPostCode={program_code}"
        )
        session.post(
            ACORN_URL + f"/removeProgramEntry?tabIndex={tab}&postCode={program_code}"
        )

        response.raise_for_status()

        req_json = json.dumps(response.json())

        with get_db_pool().connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                INSERT INTO bronze_program_data (id, name, json, status)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (id) DO UPDATE SET
                    name = EXCLUDED.name,
                    json = EXCLUDED.json,
                    status = EXCLUDED.status,
                    last_seen = CURRENT_TIMESTAMP,
                    updated = CASE 
                        WHEN bronze_program_data.json IS DISTINCT FROM EXCLUDED.json 
                        THEN CURRENT_TIMESTAMP 
                        ELSE bronze_program_data.updated 
                    END
                """,
                    (program_code + "-" + CATALOG_YEAR, program, req_json, "EXTRACTED"),
                )
    finally:
        return_cookie(headers, tab)
from __future__ import annotations
import requests
from utils import get_dx_headers, get_session, return_cookie
from constants import ACORN_URL, DEGREE_CORD
from database import get_db_pool
import json
import os

def pull_prereqs(id: str):
    try:
        session = get_session()
        tab, headers = get_dx_headers()
        session.headers.update(headers)

        row, col = DEGREE_CORD
        course = id[0:8]
        response = session.post(
            ACORN_URL
            + f"saveCourseEntry?tabIndex={tab}&selRowIndex={row}&selColIndex={col}&newCourseCode={course}",
            json={},
        )

        response.raise_for_status()

        response = session.get(
            ACORN_URL + f"getCellDetails?tabIndex={tab}&rowIndex={row}&colIndex={col}"
        )

        response.raise_for_status()

        session.post(
            ACORN_URL + f"deleteCourseEntry?tabIndex={tab}&selRowIndex={row}&selColIndex={col}",
            json={},
        )
        
        prereq_json = json.dumps(response.json())

        with get_db_pool().connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    UPDATE bronze_course_data
                    SET last_seen = CURRENT_TIMESTAMP, is_active = TRUE, prereq_json = %s, status = %s,
                    updated = CASE
                        WHEN bronze_course_data.prereq_json IS DISTINCT FROM %s THEN CURRENT_TIMESTAMP
                        ELSE bronze_course_data.updated
                    END
                    WHERE id = %s
                    """,
                    (prereq_json, "PREREQS PULLED", prereq_json, id),
                )

            if cur.rowcount == 0:
                raise ValueError(f"{course, id} not found in bronze course data")
    finally:
        return_cookie(headers, tab)
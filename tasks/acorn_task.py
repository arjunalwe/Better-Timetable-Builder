from __future__ import annotations
import requests
from utils import get_acorn_headers
from constants import ACORN_URL, DEGREE_CORD
from database import pool
import json


def pull_from_acorn(id: str, course: str):
    headers = get_acorn_headers()

    row, col = DEGREE_CORD
    session = requests.Session()
    session.headers.update(headers)
    response = session.post(
        ACORN_URL
        + f"saveCourseEntry?tabIndex=0&selRowIndex={row}&selColIndex={col}&newCourseCode={course}",
        json={},
    )

    response.raise_for_status()

    session.post(ACORN_URL + "reassessPlan?tabIndex=0", json={})
    response = session.get(
        ACORN_URL + f"getCellDetails?tabIndex=0&rowIndex={row}&colIndex={col}"
    )

    response.raise_for_status()

    session.post(
        ACORN_URL + f"deleteCourseEntry?tabIndex=0&selRowIndex={row}&selColIndex={col}",
        json={},
    )

    with pool.connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                UPDATE bronze
                SET acorn_json = %s, status = %s, updated = CURRENT_TIMESTAMP
                WHERE id = %s
                """,
                (json.dumps(response.json()), "ACORN COMPLETED", id),
            )

        conn.commit()
        if cur.rowcount == 0:
            raise ValueError(f"{course, id} not found in bronze")
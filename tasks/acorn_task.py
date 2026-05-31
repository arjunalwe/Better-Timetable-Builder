from __future__ import annotations
import requests
from utils import get_acorn_headers
from constants import ACORN_URL, DB_URL

# TODO: auto cookie handling 
cookie = ""
headers = get_acorn_headers(cookie)

def get_prereqs(course: str):
    # TODO: UPDATE COLUMN LOGIC
    row, col = 0, 3
    session = requests.Session()
    session.headers.update(headers)
    response = session.post(
        ACORN_URL
        + f"saveCourseEntry?tabIndex=0&selRowIndex={row}&selColIndex={col}&newCourseCode={course}",
        json={},
    )
        
    session.post(ACORN_URL + "reassessPlan?tabIndex=0", json={})
    response = session.get(
        ACORN_URL + f"getCellDetails?tabIndex=0&rowIndex={row}&colIndex={col}"
    )
    session.post(
        ACORN_URL + f"deleteCourseEntry?tabIndex=0&selRowIndex={row}&selColIndex={col}",
        json={},
    )
    
    # TODO: PUSH JSON TO DB
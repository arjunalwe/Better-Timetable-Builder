import requests
from constants import REFERENCE_URL, TTB_URL, HEADERS_TTB, HEADERS_ACORN, ACORN_URL
import re
import os
from config import conn as redis_conn
from config import program_queue
from rq import Queue
import time

def get_references() -> dict:
    reference = requests.get(REFERENCE_URL, headers=HEADERS_TTB)

    return reference.json()["payload"]

def build_payload() -> dict:
    data = get_references()
    sessions = [
        i["value"]
        for i in data["currentSessions"]
        if any(c.isdigit() for c in i["value"])
    ]

    divisions = [i["value"] for i in data["divisions"]]

    return {
        "courseCodeAndTitleProps": {
            "courseCode": "",
            "courseTitle": "",
            "courseSectionCode": "",
            "searchCourseDescription": True,
        },
        "departmentProps": [],
        "campuses": [],
        "sessions": sessions,
        "requirementProps": [],
        "instructor": "",
        "courseLevels": [],
        "deliveryModes": [],
        "dayPreferences": [],
        "timePreferences": [],
        "divisions": divisions,
        "creditWeights": [],
        "availableSpace": False,
        "waitListable": False,
        "page": 1,
        "pageSize": 5,
        "direction": "asc",
    }

def get_total_pages() -> int:    
    payload = build_payload()
    
    response = requests.post(TTB_URL, json=payload, headers=HEADERS_TTB)
    
    return response.json()["payload"]["pageableCourse"]["total"] // 20 + 1


_session = None
_session_pid = None

def get_session() -> requests.Session:
    global _session, _session_pid
    current_pid = os.getpid()

    if _session is None or _session_pid != current_pid:
        if _session is not None:
            _session.close()
            
        _session = requests.Session()
        _session_pid = current_pid
        
    return _session


def get_dx_headers():
    headers = HEADERS_ACORN.copy()
    response = redis_conn.blpop("acorn_cookies", timeout=10)
        
    raw_cookie_string = response[1].decode("utf-8")
    
    tab, cookie = raw_cookie_string.split("|")    
    
    headers["Cookie"] = cookie
    headers["X-XSRF-TOKEN"] = re.search(r"XSRF-TOKEN=([^;]+)", cookie).group(1)
    
    return tab, headers


def get_programs() -> list[str]:
    tab, headers = get_dx_headers()
    session = get_session()
    
    session.headers.update(headers)
    
    as_response = session.get(ACORN_URL + f"programSuggestions?searchText=AS")
    ah_response = session.get(ACORN_URL + f"programSuggestions?searchText=AH")
    
    as_response.raise_for_status()
    ah_response.raise_for_status()
    
    return_cookie(headers, tab)
    
    return as_response.json() + ah_response.json()


def return_cookie(headers: str, tab: str):
    redis_conn.lpush("acorn_cookies", f"{tab}|{headers['Cookie']}")

 
def pause_until_queue(timeout: int, *queues: Queue):
    while any(len(q) > 0 or q.started_job_registry.get_job_count() > 0 for q in queues):
        time.sleep(timeout)
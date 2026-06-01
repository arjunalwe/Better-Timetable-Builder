import requests
from constants import REFERENCE_URL, TTB_URL, HEADERS_TTB, HEADERS_ACORN
import re
import os
from dotenv import load_dotenv

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


def get_acorn_headers():
    headers = HEADERS_ACORN.copy()
    load_dotenv()
    cookie = os.environ.get("ACORN_COOKIE")
    
    headers["Cookie"] = cookie
    headers["X-XSRF-TOKEN"] = re.search(r"XSRF-TOKEN=([^;]+)", cookie).group(1)
    
    return headers
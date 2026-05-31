from __future__ import annotations
import requests
import itertools
import time
import re
import json
from pprint import pprint

cookie = "_ga_9H2P504YR1=GS2.1.s1755903368$o1$g1$t1755905139$j60$l0$h0; _ga=GA1.1.1710729026.1755903368; _ga_JQDSE1YPEX=GS2.1.s1755913336$o1$g1$t1755913404$j58$l0$h0; redirectUrl=https://www.acorn.utoronto.ca/degree-explorer/dx-session-expired/; LtpaToken2=Q3ZUSiCEGyRSM25gsjl/Y5Pm8L/EZtoakjcqYWNW3B6jl7G3y6UeJRnIYzKswybsQSbdK790ALEytxBWwHp+ol2LFcmP26eUdHtyqTSM7qYmRHFgJ2qdLpXJEj94xd/0l+W7Skw5yVP/YiBnD8ZjUOhbvndzoIhx4lVatDKt1yjux/Nn0+fSWFDr1TRSj14FPVbSIn4U5iRqu/oZy3uRX0o6swqQ9/Z6wDgJ7O9FMGMpIpNS4G4uq6yj2zZBiD1dT4WrrG1m7wp8I7UP2amieYSEGpILAheA6b65+3xN19fXMAl/TOT2+1MNc5MyL3rU6fctVJfAUyDYGXQEXerPhyvTwM/P0rfI6r3mlbx1d9Z6Le2HJli04tszA+u0V6n6wel6quUS37oIZ4xB8nnBbe9Qdr9UV4UxClzt0TWt5VbjBIzNSB84hvw8gXrOxWts; JSESSIONID=0000bnWTTEF1Y7Y3N70xAFBCQJulHi4:DXSTUDENT-LBRT-PROD2; WSJSESSIONID=aa:DXSTUDENT-LBRT-PROD2; XSRF-TOKEN=rwsqyAkqrJJBFD325dD4vFsyV3+1u4uPtHoXHiIIJ3I="
token = re.search(r"XSRF-TOKEN=([^;]+)", cookie).group(1)

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "Content-Type": "text/plain",
    "Cookie": cookie,
    "X-XSRF-TOKEN": token,
    "Origin": "https://degreeexplorer.utoronto.ca",
    "Referer": "https://degreeexplorer.utoronto.ca/degreeExplorer/planner",
}


def get_prereqs(course: str):
    row, col = 0, 3
    session = requests.Session()
    session.headers.update(headers)
    response = session.post(
        de_url
        + f"saveCourseEntry?tabIndex=0&selRowIndex={row}&selColIndex={col}&newCourseCode={course}",
        json={},
    )
    pprint(f"POST {course}: {response.status_code}")
    session.post(de_url + "reassessPlan?tabIndex=0", json={})
    response = session.get(
        de_url + f"getCellDetails?tabIndex=0&rowIndex={row}&colIndex={col}"
    )
    session.post(
        de_url + f"deleteCourseEntry?tabIndex=0&selRowIndex={row}&selColIndex={col}",
        json={},
    )
    pprint(f"GET {course}: {response.status_code}")
    return (
        parse_prereq(response.json()["prerequisites"], "P"),
        parse_prereq(response.json()["corequisites"], "C"),
        parse_prereq(["exclusions"], "E"),
    ), parse_prereq(["orderedExclusions"], "OE")


def parse_prereq(data: dict, type: str) -> tuple[dict[str : str | list], bool]:
    manual_review = False
    courses = {}
    referenced_nodes = set()
    for i in data:
        manual_review = False
        if i["countType"] == "GRADE":
            manual_review = True
            grade = i["targetValue"]
            p = courses[i["displaySuffix"][-2:]]["requisiteItems"]
            for j in i["requisiteItems"]:
                for k in p:
                    if k["code"] == j["code"]:
                        k["grade"] = grade
            continue

        elif i["countType"] == "FCES" and i["count"] > 1.0:
            for j in i["requisiteItems"]:
                j["grade"] = i["count"]

        curr = i["shortIdentifier"]
        curr = str.strip(curr, "()") if curr[0] == "(" else curr
        courses[curr] = i
        for j in i["requisiteItems"]:
            if not j["courseEntity"]:
                referenced_nodes.add(j["code"])

    roots = {k for k in set.difference(set(courses.keys()), referenced_nodes)}

    if len(roots) > 1:
        p = {"logic": "AND", "groups": []}
        for i in roots:
            p["groups"].append(
                build_dict(
                    courses[i]["type"],
                    courses[i]["requisiteItems"],
                    courses,
                    courses[i]["countType"],
                )
            )
        return (p, manual_review)

    elif len(roots) == 1:
        p = build_dict(
            courses[type + "1"]["type"],
            courses[type + "1"]["requisiteItems"],
            courses,
            courses[type + "1"]["countType"],
        )
        return (p, manual_review)

    else:
        print("Empty")
        return ({}, manual_review)


def build_dict(
    log_str: str, requisite_items: list[dict], courses: dict[str, dict], countType: str
):
    p = {"logic": eval_log_str(log_str), "groups": []}

    if countType == "FCES" and p["logic"] == "OR":
        requisite_items = return_fce_groups(requisite_items)

    for i in requisite_items:
        if type(i) == tuple:
            p["groups"].append(
                build_dict(invert_log_str(log_str), i, courses, countType)
            )

        else:
            if i["courseEntity"]:
                try:
                    p["groups"].append((i["code"], i["grade"]))
                except KeyError:
                    p["groups"].append((i["code"], 50))

            elif not i["courseEntity"] and len(i["code"]) == 2:
                p["groups"].append(
                    build_dict(
                        courses[i["code"]]["type"],
                        courses[i["code"]]["requisiteItems"],
                        courses,
                        "",
                    )
                )

            else:
                p["groups"].append((i["display"], i.get("grade")))

    return p


def return_fce_groups(courses: list):
    course_suffixes = {
        0.5: [course for course in courses if course.get("code", "")[6:7] == "H"],
        1.0: [course for course in courses if course.get("code", "")[6:7] == "Y"],
        0.0: [course for course in courses if course.get("code", "")[6:7] not in "HY"],
    }
    if course_suffixes[0.5] != [] and course_suffixes[1.0] != []:
        return (
            list(itertools.combinations(course_suffixes[0.5], 2))
            + course_suffixes[1.0]
            + course_suffixes[0.0]
        )

    else:
        return courses


def eval_log_str(log_str: str):
    return "OR" if log_str == "MINIMUM" or log_str == "ANY" else "AND"


def invert_log_str(op: str):
    return "OR" if op == "AND" else "AND"

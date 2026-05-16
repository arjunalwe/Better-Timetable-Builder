from __future__ import annotations
import requests
import itertools
import time
import re
import json
from pprint import pprint

de_url = "https://degreeexplorer.utoronto.ca/degreeExplorer/rest/dxPlanner/"

cookie = "_ga_9H2P504YR1=GS2.1.s1755903368$o1$g1$t1755905139$j60$l0$h0; _ga=GA1.1.1710729026.1755903368; _ga_JQDSE1YPEX=GS2.1.s1755913336$o1$g1$t1755913404$j58$l0$h0; redirectUrl=https://www.acorn.utoronto.ca/degree-explorer/dx-session-expired/; LtpaToken2=Q3ZUSiCEGyRSM25gsjl/Y5Pm8L/EZtoakjcqYWNW3B6jl7G3y6UeJRnIYzKswybsQSbdK790ALEytxBWwHp+ol2LFcmP26eUdHtyqTSM7qaseD4qtA/uZxZX0tHZsteYCG5M92/FLQzjP5FuEw8Xsl5JvlvdT8qHcLxWMZxqYdVdj+2DvhYkvPdPOrhoBbcLDf1jH9FJRbwfjB1NuH+V0jmG1DVYbGoejOKsJV+/afg/akG0oLOeb3A+5Lj79ubkHvf4glU9inZOAcazK2duooVHgGX0ikXPztlGIY4MGhhHbsbJBBgAworPZzBWJoMElwwoa2oLENW2H0lklL4G1h4VKNcEwGv5eYhnT5lNANuzlHjATZGfpD+aXefJKjWdZ4Z6YGvmXke+XZLW+HQebVSH8evnrKQEliVSNQv9zQCm4YUVFHd1vH0v0gdDoNAy; JSESSIONID=0000Wk0WM4e0Via0GgjHVWiusOFrCFe:DXSTUDENT-LBRT-PROD1; WSJSESSIONID=aa:DXSTUDENT-LBRT-PROD1; XSRF-TOKEN=ucJdnQLE+j/phDh8FrHflY7uNymWt20erFn1thHKfIY="
token = re.search(r'XSRF-TOKEN=([^;]+)', cookie).group(1)

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
    response = session.post(de_url + f"saveCourseEntry?tabIndex=0&selRowIndex={row}&selColIndex={col}&newCourseCode={course}", json={})
    pprint(f"POST {course}: {response.status_code}")
    session.post(de_url + "reassessPlan?tabIndex=0", json={})
    response = session.get(de_url + f"getCellDetails?tabIndex=0&rowIndex={row}&colIndex={col}")
    session.post(de_url + f"deleteCourseEntry?tabIndex=0&selRowIndex={row}&selColIndex={col}", json={})
    pprint(response.json())
    pprint(f"GET {course}: {response.status_code}")
    return parse_prereq(response.json()["prerequisites"])

def parse_prereq(data: dict) -> tuple[dict[str: str | list], bool]:
    courses = {}
    referenced_nodes = set()
    manual_review = False
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
            p["groups"].append(build_dict(courses[i]["type"], courses[i]["requisiteItems"], courses, courses[i]["countType"]))
        return (p, manual_review)
            
    elif len(roots) == 1:
        p = build_dict(courses["P1"]["type"], courses["P1"]["requisiteItems"], courses, courses["P1"]["countType"])
        return (p, manual_review)
    
    else:
        print("Empty")
        return ({}, manual_review)
    

def build_dict(log_str: str, requisite_items: list[dict], courses: dict[str, dict], countType: str):
    p = {"logic": eval_log_str(log_str), "groups": []}

    if countType == "FCES" and p["logic"] == "OR":
        requisite_items = return_fce_groups(requisite_items)
    
    for i in requisite_items:
        if type(i) == tuple:
            p["groups"].append(build_dict(invert_log_str(log_str), i, courses, countType))
        
        else:
            if i["courseEntity"]:
                try:
                    p["groups"].append((i["code"], i["grade"]))
                except KeyError:
                    p["groups"].append((i["code"], 50))
                
            elif not i["courseEntity"] and len(i["code"]) == 2: 
                p["groups"].append(build_dict(courses[i["code"]]["type"], courses[i["code"]]["requisiteItems"], courses, ""))
            
            else:
                p["groups"].append((i["display"], i.get("grade")))
        
    return p

def return_fce_groups(courses: list):
    course_suffixes = {
        0.5: [course for course in courses if course["code"][6] == "H"],
        1.0: [course for course in courses if course["code"][6] == "Y"],
        0.0: [course for course in courses if course["code"][6] not in "HY"]
    }    
    if course_suffixes[0.5] != [] and course_suffixes[1.0] != []:
        return list(itertools.combinations(course_suffixes[0.5], 2)) + course_suffixes[1.0] + course_suffixes[0.0]
        
    else:
        return courses
        
def eval_log_str(log_str: str):
    return "OR" if log_str == "MINIMUM" else "AND"

def invert_log_str(op: str):
    return "OR" if op == "AND" else "AND"


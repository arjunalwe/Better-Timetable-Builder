from __future__ import annotations
import requests
import itertools
import json
from pprint import pprint

de_url = "https://degreeexplorer.utoronto.ca/degreeExplorer/rest/dxPlanner/"

cookie = "_ga_9H2P504YR1=GS2.1.s1755903368$o1$g1$t1755905139$j60$l0$h0; _ga=GA1.1.1710729026.1755903368; _ga_JQDSE1YPEX=GS2.1.s1755913336$o1$g1$t1755913404$j58$l0$h0; redirectUrl=https://www.acorn.utoronto.ca/degree-explorer/dx-session-expired/; LtpaToken2=Q3ZUSiCEGyRSM25gsjl/Y5Pm8L/EZtoakjcqYWNW3B6jl7G3y6UeJRnIYzKswybsQSbdK790ALEytxBWwHp+ol2LFcmP26eUdHtyqTSM7qaseD4qtA/uZxZX0tHZsteYGRe7jn7RtZAANcaNxuismY9uw3kxLgA5PcVbZ3b1+hdNNTN6WIb/nj9af303h7atJrlTX8hovfoQVxjxxMpKy+Tl5L++PR577BnCVjI57bDU4+7ItboNrwKeTdwnblw47BbyT/4JIe07X+orHLLmiDfcwG2CeARs0Cl82rfGcdBQii1JcnpqsPwg4jV/c84WE/pSoqFnjeFHDZBW6S0gPspMFQcG+TAZuiXF4THeHqA+RaZbqak1O6WMl7IAUmhC7LGP6f4gham5WTrhCcSpHFptTnbFpk+N+HBBz2tlLnvT8irBP1HODZmDo7u53i/t; JSESSIONID=00004BGo2HMnT5uQOcYixQzUZ8uV0ue:DXSTUDENT-LBRT-PROD1; WSJSESSIONID=aa:DXSTUDENT-LBRT-PROD1; XSRF-TOKEN=Wd1f6SO/TFf/PKlM2yh/Frmrn3/2Hdgm+3cS+oJyGlM="

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "application/json",
    "Cookie": cookie,
    "Origin": "https://degreeexplorer.utoronto.ca",
    "Referer": "https://degreeexplorer.utoronto.ca/degreeExplorer/planner",
}

def get_prereqs(course: str):
    row, col = 0, 3
    session = requests.Session()
    session.headers.update(headers)
    session.post(de_url + f"saveCourseEntry?tabIndex=0&selRowIndex={row}&selColIndex={col}&newCourseCode={course}", headers=headers)
    session.post(de_url + "reassessPlan?tabIndex=0", headers=headers)
    response = session.get(de_url + f"getCellDetails?tabIndex=0&rowIndex={row}&colIndex={col}", headers=headers)
    session.post(de_url + f"deleteCourseEntry?tabIndex=0&selRowIndex={row}&selColIndex={col}", headers=headers)
    
    return parse_prereq(response.json()["prerequisites"])

def parse_prereq(data: dict) -> dict[str: str | list]:
    courses = {}
    referenced_nodes = set()
    for i in data:
        if i["countType"] == "GRADE":
            grade = i["targetValue"]
            p = courses[i["displaySuffix"][-2:]]["requisiteItems"]
            for j in i["requisiteItems"]:
                for k in p:
                    if k["code"] == j["code"]:
                        k["grade"] = grade
            continue
                
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
        return p
            
    elif len(roots) == 1:
        p = build_dict(courses["P1"]["type"], courses["P1"]["requisiteItems"], courses, courses["P1"]["countType"])
        return p
    
    else:
        return {}
    

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
                
            else: 
                p["groups"].append(build_dict(courses[i["code"]]["type"], courses[i["code"]]["requisiteItems"], courses, ""))
        
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


pprint(get_prereqs("MAT237Y1"))

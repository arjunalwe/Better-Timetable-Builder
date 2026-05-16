import requests
import itertools
import json
from pprint import pprint

de_url = "https://degreeexplorer.utoronto.ca/degreeExplorer/rest/dxPlanner/"

cookie = "_ga_9H2P504YR1=GS2.1.s1755903368$o1$g1$t1755905139$j60$l0$h0; _ga=GA1.1.1710729026.1755903368; _ga_JQDSE1YPEX=GS2.1.s1755913336$o1$g1$t1755913404$j58$l0$h0; redirectUrl=https://www.acorn.utoronto.ca/degree-explorer/dx-session-expired/; LtpaToken2=Q3ZUSiCEGyRSM25gsjl/Y5Pm8L/EZtoakjcqYWNW3B6jl7G3y6UeJRnIYzKswybsQSbdK790ALEytxBWwHp+ol2LFcmP26eUdHtyqTSM7qaseD4qtA/uZxZX0tHZsteYx1u+NUyNBJ/8qlUZoMGy+QQhIFvtje6mZQWVtqispU5GVj8Iyk2PZLQsdZPdQ3nnk84oYarUszQqjoM7NzLxt2iXS3mWai4EqRp3XsyLtG/QMaD28jqbkXKggItlQsi5FHnq7Vx4OH29q93WdErwXBnVOAYD1Pph6aCiVl9gQQ1HXSoKmiCwvINvHvE81ftlkj3S4ZU2Dq0IewRB7z0AEnZpSYIc/f/WVBPLA9c83Na/mPxY2pBGhvnooFRUgXvkhk1c6iWxbnkqTDrkUSyia8Krpbi+eHpTeWIzz5Nox6IdkzkmQ1EkcHxHrVrHqwgm; JSESSIONID=0000j_LlVBRVZ7B1kMhp2I1AZvdWCS4:DXSTUDENT-LBRT-PROD2; WSJSESSIONID=aa:DXSTUDENT-LBRT-PROD2; XSRF-TOKEN=+mjmDO5nYLrfNYS1kiJl4tO63QjOTAgBoOgpx76WJ+o="

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "application/json",
    "Cookie": cookie,
    "Origin": "https://degreeexplorer.utoronto.ca",
    "Referer": "https://degreeexplorer.utoronto.ca/degreeExplorer/planner",
}


class PrerequisiteTree:
    
    def __init__(self, logic, groups):
        self.logic = logic
        self.groups = groups
        
        
    def get_dict(self):
        str_groups = []
        for i in self.groups:
            if type(i) is PrerequisiteTree:
                str_groups.append(i.get_dict())
            else:
                str_groups.append(i)
        
        dih = {
                "logic": self.logic,
                "groups": str_groups
            }
            
        return dih


def get_prereqs(course: str):
    row, col = 0, 3
    requests.post(de_url + f"saveCourseEntry?tabIndex=0&selRowIndex={row}&selColIndex={col}&newCourseCode={course}", headers=headers)
    requests.post(de_url + "reassessPlan?tabIndex=0", headers=headers)
    response = requests.get(de_url + f"getCellDetails?tabIndex=0&rowIndex={row}&colIndex={col}", headers=headers)
    requests.post(de_url + f"deleteCourseEntry?tabIndex=0&selRowIndex={row}&selColIndex={col}", headers=headers)
    
    return response.json()


def recurse(log_str: str, requisite_items: list[dict], courses: dict[str, dict], countType: str):
    p = PrerequisiteTree(eval_log_str(log_str), [])

    if len(requisite_items) == 1:
        p.groups.append(requisite_items[0]["code"])
        return p
    
    if countType == "FCES" and p.logic == "OR":
        requisite_items = return_fce_groups(requisite_items)
    
    for i in requisite_items:
        if type(i) == tuple:
            p.groups.append(recurse(invert_log_str(log_str), i, courses, countType))
        
        else:
            if i["courseEntity"]:
                p.groups.append(i["code"])
                
            else: 
                p.groups.append(recurse(courses[i["code"]]["type"], courses[i["code"]]["requisiteItems"], courses, ""))
        
    return p
        
        
def eval_log_str(log_str: str):
    return "OR" if log_str == "MINIMUM" else "AND"

def invert_log_str(op: str):
    return "OR" if op == "AND" else "AND"


def contains_pointers(requisite_items: list):
    return any([i["courseEntity"] for i in requisite_items])

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


with open('sample_acorn_prereq_phy252.json', 'r') as file:
    data = json.load(file)
    courses = {}
    referenced_nodes = set()
    for i in data["prerequisites"]:
        curr = i["shortIdentifier"]
        curr = str.strip(curr, "()") if curr[0] == "(" else curr
        courses[curr] = i
        for j in i["requisiteItems"]:
            if not j["courseEntity"]:
                referenced_nodes.add(j["code"])
    
    roots = {k for k in set.difference(set(courses.keys()), referenced_nodes)}

    if len(roots) > 1:
        p = PrerequisiteTree("AND", [])
        for i in roots:
            p.groups.append(recurse(courses[i]["type"], courses[i]["requisiteItems"], courses, courses[i]["countType"]))
            
    else:
        p = recurse(courses["P1"]["type"], courses["P1"]["requisiteItems"], courses, courses["P1"]["countType"])
    
    pprint(p.get_dict())
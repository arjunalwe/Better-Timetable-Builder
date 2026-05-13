import requests
import itertools
import json

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


def recurse(log_str: str, requisite_items: list[dict], courses: dict[str, dict]):
    p = PrerequisiteTree(eval_log_str(log_str), [])
    for i in requisite_items:
        if i["courseEntity"]:
            p.groups.append(i["code"])
        
        else:
            p.groups.append(recurse(courses[i["code"]]["type"], courses[i["code"]]["requisiteItems"], courses))
        
    return p
        
        
def eval_log_str(log_str: str):
    return "OR" if log_str == "MINIMUM" else "AND"


def contains_pointers(requisite_items: list):
    return any([i["courseEntity"] for i in requisite_items])

def return_fce_groups(fce: float, courses: list):
    course_suffixes = {
        0.5: [course for course in courses if course[7] == "F"],
        1.0: [course for course in courses if course[7] == "Y"]
    }
    
    if course_suffixes[0.5] != [] and course_suffixes[1.0] != []:
        if fce == 1.0:
            return list(itertools.combinations(course_suffixes[0.5], 2)) + course_suffixes[1.0]
        
        else:
            return courses
    

with open('sample_acorn_prereq_phy252.json', 'r') as file:
    data = json.load(file)
    courses = {}
    for i in data["prerequisites"]:
        curr = i["shortIdentifier"]
        curr = str.strip(curr, "()") if curr[0] == "(" else curr
        courses[curr] = i
    
    if len(courses) > 1:
        p = PrerequisiteTree("OR", [])
        for i in courses:
            p.groups.append(recurse(courses[i]["type"], courses[i]["requisiteItems"], courses))
            
    else:
        p = recurse(courses["P1"]["type"], courses["P1"]["requisiteItems"], courses)
    
    
    import pprint
    pprint.pprint(p.get_dict())
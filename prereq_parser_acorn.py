import requests
import json

de_url = "https://degreeexplorer.utoronto.ca/degreeExplorer/rest/dxPlanner/"

cookie = "_ga_9H2P504YR1=GS2.1.s1755903368$o1$g1$t1755905139$j60$l0$h0; _ga=GA1.1.1710729026.1755903368; _ga_JQDSE1YPEX=GS2.1.s1755913336$o1$g1$t1755913404$j58$l0$h0; redirectUrl=https://www.acorn.utoronto.ca/degree-explorer/dx-session-expired/; LtpaToken2=Q3ZUSiCEGyRSM25gsjl/Y5Pm8L/EZtoakjcqYWNW3B6jl7G3y6UeJRnIYzKswybsQSbdK790ALEytxBWwHp+ol2LFcmP26eUdHtyqTSM7qaseD4qtA/uZxZX0tHZsteYbQxZVTnCnHRQBfuwAkHwXZRPPCuLMgL7VFdZ4IwFgkgMi7B3k1SNnVyi1/MaOp1wvHL9jGTVRGdC8hP9NYLLJgY9f4Q2RWVgjHQSTgETerIuqxjeyd0KWjm+8/tfBkkNtnU7gAlpSBArbCLZ3zpzI6mbAfQD7fmhHE799tH461reO8oXytlk0mxlPfF6ciztj8jzoKU18ML+AnhMHpno+R10uOVZ7OgFP+sYHZV39YvI+eUvLc5AEKCGbNRs2120ysnOvQV/7ZHXqWaunaIaqFhOp7PR6ONZbe5Kt2MNav96H3hZ2tWtbDmth7urr+Ji; JSESSIONID=0000t-vozCMdrpCgRQpYUiIHn5Fkc4r:DXSTUDENT-LBRT-PROD2; WSJSESSIONID=aa:DXSTUDENT-LBRT-PROD2; XSRF-TOKEN=Vuw0vF5z5ZskjIHqSNafxdKhiRMXRCPyNy+gwlEVFa8="

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "application/json",
    "Cookie": cookie,
    "Origin": "https://degreeexplorer.utoronto.ca",
    "Referer": "https://degreeexplorer.utoronto.ca/degreeExplorer/planner",
}

def get_prereqs(course):
    row, col = 0, 3
    requests.post(de_url + f"saveCourseEntry?tabIndex=0&selRowIndex={row}&selColIndex={col}&newCourseCode={course}", headers=headers)
    requests.post(de_url + "reassessPlan?tabIndex=0", headers=headers)
    response = requests.get(de_url + f"getCellDetails?tabIndex=0&rowIndex={row}&colIndex={col}", headers=headers)
    requests.post(de_url + f"deleteCourseEntry?tabIndex=0&selRowIndex={row}&selColIndex={col}", headers=headers)
    
    print(f"Response Code: {response.status_code}")
    return response.json()



with open('sample_acorn_prereq_response.json', 'r') as file:
    data = json.load(file)
    print([[j["code"] for j in i["requisiteItems"]] for i in data["prerequisites"]])
    
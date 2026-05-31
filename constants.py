REFERENCE_URL = "https://api.easi.utoronto.ca/ttb/reference-data"
TTB_URL = "https://api.easi.utoronto.ca/ttb/getPageableCourses"
DB_URL = "postgresql://admin:password@localhost:5432/uoft_courses"
ACORN_URL = "https://degreeexplorer.utoronto.ca/degreeExplorer/rest/dxPlanner/"

HEADERS_TTB = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Origin": "https://ttb.utoronto.ca",
        "Referer": "https://ttb.utoronto.ca/",
    }   

HEADERS_ACORN = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "Content-Type": "text/plain",
    "Cookie": "",
    "X-XSRF-TOKEN": "",
    "Origin": "https://degreeexplorer.utoronto.ca",
    "Referer": "https://degreeexplorer.utoronto.ca/degreeExplorer/planner",
}
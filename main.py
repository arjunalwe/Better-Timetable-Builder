import requests
from constants import ACORN_URL
from constants import TTB_URL, HEADERS_TTB, REFERENCE_URL, MIN_FETCH_INTERVAL
from database import get_db_pool

# cookie = "_ga_9H2P504YR1=GS2.1.s1755903368$o1$g1$t1755905139$j60$l0$h0; _ga=GA1.1.1710729026.1755903368; _ga_JQDSE1YPEX=GS2.1.s1755913336$o1$g1$t1755913404$j58$l0$h0; cf_clearance=mBkwLj5vM.h4Q._Jq96R_KV7Kvz7EjOQdxRE7Pl5vD8-1780612508-1.2.1.1-rqeZMFVqEHMfPgyvPUAyhnBNnJthffzQKwLU5Ts3JBik.1eBWxrFuM4TUTK5piVRDuksGUozH.Cg86fhsWkrtGASsZBK7d3QClSOqkV.COIsKJ0ptuYlDYioULGQegPVZN1z4ywgw1b64BE7YrTPlq3GSWeEWOgJjmgN_NXhbnpqlNQF8E45S8uBFM933AOug4CeDax3x8oJsFLfIz87x8cy6Pdv0XO_.cnNhp5VvzaAsU74AtetaQegtq5DVFPLWqWXjzeUfomyAC7uSf4KilF0tbWcusReb2GCWuVeEEiPa.LPlMkCIBv7xysJpZ1k9_G3R.YBeNudN6mBxLzT.A; redirectUrl=https://www.acorn.utoronto.ca/degree-explorer/dx-session-expired/; LtpaToken2=Q3ZUSiCEGyRSM25gsjl/Y5Pm8L/EZtoakjcqYWNW3B6jl7G3y6UeJRnIYzKswybsQSbdK790ALEytxBWwHp+ol2LFcmP26eUdHtyqTSM7qYCXkmJqfVHFiRJhssJzqMbYgMyVRWXd0RyCdJfS18i1lIsSiti2o2aknFOs1/h2ydULFq16P9ayrXNHKeggL3CPbn9AR/ZmFFcC9TMKm+aVQtpIE487YWMu9fj5xOeKnWEwJZ74Dxny8K4Yz6jQy2rDmM+LVgekBLwYrQ2KFxJUxD+RWlPAeTz2cs2+ipq/DIdTdM1sfZoeVwEvOs4LMex2bK56lUH/fMz3AIKEefgsgyeOLpkuSVQv7StwTUl9OQD94GjcHdeARIbYA7m60+zeO8NpkgmLVhQJpyCvau5iK7cR5vv7uPnAtaW1LfI3e0QEiy8IUC+LbcWR3+flCN1; JSESSIONID=0000MA_36D7jlyu3Cwc5thpy6_kaxFl:DXSTUDENT-LBRT-PROD2; WSJSESSIONID=aa:DXSTUDENT-LBRT-PROD2; XSRF-TOKEN=cPMXGsfltmqWnRtqKiet2N7fAO923ub/fHh8gC0PHeQ="

# HEADERS_ACORN = {
#     "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
#     "Accept": "application/json, text/plain, */*",
#     "Content-Type": "text/plain",
#     "Cookie": cookie,
#     "X-XSRF-Token": re.search(r"XSRF-TOKEN=([^;]+)", cookie).group(1),
#     "Origin": "https://degreeexplorer.utoronto.ca",
#     "Referer": "https://degreeexplorer.utoronto.ca/degreeExplorer/planner",
# }

# response = requests.get(ACORN_URL + f"programSuggestions?searchText=AS", headers=HEADERS_ACORN)
# response.raise_for_status()
# data = response.text

# print(data)

with get_db_pool("postgresql://admin:password@localhost:5432/uoft_courses").connection() as conn:
    with conn.cursor() as cur:
        cur.execute("""
                    SELECT id FROM bronze_course_data 
                    WHERE prereq_json IS NULL 
                    OR updated <= CURRENT_TIMESTAMP - CAST (%s as INTERVAL);
                    """, (MIN_FETCH_INTERVAL,)) 
        
        courses = cur.fetchall()
        print(courses)
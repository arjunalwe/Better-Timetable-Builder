import requests
import json

course_code = ""

save_url = "https://degreeexplorer.utoronto.ca/degreeExplorer/rest/dxPlanner/saveProgramEntry?tabIndex=0&newPostCode="
del_url = "https://degreeexplorer.utoronto.ca/degreeExplorer/rest/dxPlanner/removeProgramEntry?tabIndex=0&postCode="

HEADERS_ACORN = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "Content-Type": "text/plain",
    "Cookie": "_ga_9H2P504YR1=GS2.1.s1755903368$o1$g1$t1755905139$j60$l0$h0; _ga=GA1.1.1710729026.1755903368; _ga_JQDSE1YPEX=GS2.1.s1755913336$o1$g1$t1755913404$j58$l0$h0; cf_clearance=mBkwLj5vM.h4Q._Jq96R_KV7Kvz7EjOQdxRE7Pl5vD8-1780612508-1.2.1.1-rqeZMFVqEHMfPgyvPUAyhnBNnJthffzQKwLU5Ts3JBik.1eBWxrFuM4TUTK5piVRDuksGUozH.Cg86fhsWkrtGASsZBK7d3QClSOqkV.COIsKJ0ptuYlDYioULGQegPVZN1z4ywgw1b64BE7YrTPlq3GSWeEWOgJjmgN_NXhbnpqlNQF8E45S8uBFM933AOug4CeDax3x8oJsFLfIz87x8cy6Pdv0XO_.cnNhp5VvzaAsU74AtetaQegtq5DVFPLWqWXjzeUfomyAC7uSf4KilF0tbWcusReb2GCWuVeEEiPa.LPlMkCIBv7xysJpZ1k9_G3R.YBeNudN6mBxLzT.A; redirectUrl=https://www.acorn.utoronto.ca/degree-explorer/dx-session-expired/; LtpaToken2=Q3ZUSiCEGyRSM25gsjl/Y5Pm8L/EZtoakjcqYWNW3B6jl7G3y6UeJRnIYzKswybsQSbdK790ALEytxBWwHp+ol2LFcmP26eUdHtyqTSM7qYCXkmJqfVHFiRJhssJzqMbIGdS333vf0eB8bnh2X2IrhaMaZJqM4PkQRrFEjw/mWlw3gXG3OSkuhOr/yjGZAyw4OdvoriqimXVsKSHKD9h70B5iVE706r3fZmgZ/ANTbNPJqeszzfUFTdoaTBuN5DKrg/HvXyFzL/LRFLeADm+nYep+FausuP2MVRPRi2YWqNmLBGwJgx5zL6jM1v5FoDoU5jHjL7nr0YEXx9Xx1h0mSeTGJfro5YkX6D0yCkqPWioBf+DYsjAEkDtvRoBd2bSNjNBKH7roPaumn217Pgfse6HpMAbqIXSkE7jsWSWMMojcmlgSA+dzVeRD4LUlcJg; JSESSIONID=0000jlBAKmymdylvpAKKzVoqwOPdBOW:DXSTUDENT-LBRT-PROD1; WSJSESSIONID=aa:DXSTUDENT-LBRT-PROD1; XSRF-TOKEN=DrmREFZE3zjsHtKgQ6alqSMZwNJal/vRwJWkSV6hfl8=",
    "Origin": "https://degreeexplorer.utoronto.ca",
    "Referer": "https://degreeexplorer.utoronto.ca/degreeExplorer/planner",
}

response = requests.get(url, headers=HEADERS_ACORN)
data = response.text

print(data)


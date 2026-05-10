import requests
import json
import time
import psycopg

reference_url = "https://api.easi.utoronto.ca/ttb/reference-data"
post_url = "https://api.easi.utoronto.ca/ttb/getPageableCourses"
db_url = "postgresql://admin:password@localhost:5432/uoft_courses"

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Content-Type": "application/json",
    "Accept": "application/json",
    "Origin": "https://ttb.utoronto.ca",
    "Referer": "https://ttb.utoronto.ca/",
}

sessions = []
divisions = []
reference = requests.get(reference_url, headers=headers)
if reference.status_code == 200:
    data = reference.json()["payload"]
    sessions = [
        i["value"]
        for i in data["currentSessions"]
        if any(c.isdigit() for c in i["value"])
    ]
    divisions = [i["value"] for i in data["divisions"]]

payload = {
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
    "pageSize": 20,
    "direction": "asc",
}

with psycopg.connect(db_url) as conn:
    with conn.cursor() as cur:

        response = requests.post(post_url, json=payload, headers=headers)
        if response.status_code != 200:
            print("Fatal: Could not fetch initial page.")
            exit()

        num_pages = response.json()["payload"]["pageableCourse"]["total"] // 20 + 1

        cur.execute("""
            CREATE TABLE IF NOT EXISTS course_info (
                id VARCHAR(50) PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                code VARCHAR(8) NOT NULL,
                sectionCode VARCHAR(1) NOT NULL,
                campus VARCHAR(255) NOT NULL,
                sessions VARCHAR(15)[],
                sections JSONB NOT NULL,
                description TEXT,
                jsonDump JSONB NOT NULL
            );
        """)

        cur.execute("""
            CREATE TABLE IF NOT EXISTS prereq_info (
                source_code VARCHAR(15) NOT NULL,
                target_code VARCHAR(15) NOT NULL,
                type VARCHAR(25) NOT NULL,
                condition SMALLINT NOT NULL,
                req_group SMALLINT NOT NULL,
                PRIMARY KEY (source_code, target_code, type, req_group)
            );
        """)

        conn.commit()

        retry_timer = 0

        while payload["page"] <= num_pages:
            response = requests.post(post_url, json=payload, headers=headers)

            if response.status_code == 200:
                retry_timer = 0  # Reset timer on success
                data = response.json()["payload"]["pageableCourse"]["courses"]

                for c in data:
                    course_info = c.get("cmCourseInfo")
                    description = (
                        course_info.get("description") if course_info else None
                    )

                    cur.execute(
                        """
                        INSERT INTO course_info (id, name, code, sectionCode, campus, sessions, sections, description, jsonDump)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s) 
                        ON CONFLICT (id) DO UPDATE SET
                            name = EXCLUDED.name,
                            sessions = EXCLUDED.sessions,
                            sections = EXCLUDED.sections,
                            description = EXCLUDED.description,
                            jsonDump = EXCLUDED.jsonDump 
                        """,
                        (
                            c["id"],
                            c["name"],
                            c["code"],
                            c["section_code"],
                            c["campus"],
                            c.get("sessions", []),
                            json.dumps(c.get("sections", [])),
                            description,
                            json.dumps(c),
                        ),
                    )
                    
                    cur.execute(
                        """
                        INSERT INTO prereq_info (source_code, target_code, type, condition, req_group)
                        VALUES (%s, %s, %s, %s, %s)
                        ON CONFLICT (source_code, target_code, type, req_group) DO UPDATE SET
                            condition = EXCLUDED.condition,
                        """,
                        (
                            c["code"],
                            
                        )
                    )

                conn.commit()
                payload["page"] += 1

            else:
                if retry_timer < 3:
                    retry_timer += 1
                    time.sleep(2)
                    continue
                else:
                    retry_timer = 0
                    payload["page"] += 1

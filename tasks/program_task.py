from requests.exceptions import HTTPError
from utils import get_dx_headers, get_session, return_cookie
import json
import re
from constants import ACORN_URL, CATALOG_YEAR
from database import get_db_pool

def pull_programs(program: str):
    tab, headers = get_dx_headers()
    session = get_session()

    try:
        session.headers.update(headers)

        program_code = program.split("-")[0].strip()
        codes_to_delete = [program_code]

        response = session.post(
            ACORN_URL + f"/saveProgramEntry?tabIndex={tab}&newPostCode={program_code}"
        )

        if response.status_code == 500 and "Requires enrolment in parent program" in response.text:
            pattern = r"(?<=Requires enrolment in parent program )\w+"
            parent_program = re.search(pattern, response.text).group(0)

            session.post(
                ACORN_URL + f"/saveProgramEntry?tabIndex={tab}&newPostCode={parent_program}"
            )
            codes_to_delete.append(parent_program)

            response = session.post(
                ACORN_URL + f"/saveProgramEntry?tabIndex={tab}&newPostCode={program_code}"
            )

        response.raise_for_status()
        req_json = json.dumps(response.json())

        for code in reversed(codes_to_delete):
            session.post(
                ACORN_URL + f"/removeProgramEntry?tabIndex={tab}&postCode={code}"
            )

        with get_db_pool().connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO bronze_program_data (id, name, json, status)
                    VALUES (%s, %s, %s, %s)
                    ON CONFLICT (id) DO UPDATE SET
                        name = EXCLUDED.name,
                        json = EXCLUDED.json,
                        status = EXCLUDED.status,
                        last_seen = CURRENT_TIMESTAMP,
                        updated = CASE 
                            WHEN bronze_program_data.json IS DISTINCT FROM EXCLUDED.json 
                            THEN CURRENT_TIMESTAMP 
                            ELSE bronze_program_data.updated 
                        END
                    """,
                    (
                        program_code + "-" + str(CATALOG_YEAR),
                        program,
                        req_json,
                        "EXTRACTED",
                    ),
                )
                
    except HTTPError as error:
        print(f"\n{'='*50}", flush=True)
        print(f"FATAL API ERROR ON COURSE: {program} | TAB: {tab}", flush=True)
        if error.response is not None:
            print(error.response.text, flush=True)
        print(f"{'='*50}\n", flush=True)
        raise error

    finally:
        return_cookie(headers, tab)
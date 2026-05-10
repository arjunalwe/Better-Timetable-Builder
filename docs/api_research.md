api endpoint: https://api.easi.utoronto.ca/ttb/getPageableCourses

Headers
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Origin": "https://ttb.utoronto.ca",
        "Referer": "https://ttb.utoronto.ca/"
    }


Payload Structure
    payload = {
        "courseCodeAndTitleProps": {
            "courseCode": "",
            "courseTitle": "",
            "courseSectionCode": "",
            "searchCourseDescription": True,
        },
        "departmentProps": [],
        "campuses": [],
        "sessions": ["20265F", "20265S", "20265", "20269", "20271", "20269-20271"],
        "requirementProps": [],
        "instructor": "",
        "courseLevels": [],
        "deliveryModes": [],
        "dayPreferences": [],
        "timePreferences": [],
        "divisions": ["APSC", "ARTSC", "FIS", "FPEH", "MUSIC", "ARCLA", "ERIN", "SCAR"],
        "creditWeights": [],
        "availableSpace": False,
        "waitListable": False,
        "page": 1,
        "pageSize": 20,
        "direction": "asc",
    }


API only returns 20 courses at a time, regardless of pageSize. page is the important variable.
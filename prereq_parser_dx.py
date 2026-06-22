from __future__ import annotations
import itertools
from pprint import pprint

def parse_prereq(data: dict, type: str) -> tuple[dict[str : str | list], bool]:
    manual_review = False
    courses = {}
    referenced_nodes = set()
    for i in data:
        manual_review = False
        if i["countType"] == "GRADE":
            manual_review = True
            grade = i["targetValue"]
            p = courses[i["displaySuffix"][-2:]]["requisiteItems"]
            for j in i["requisiteItems"]:
                for k in p:
                    if k["code"] == j["code"]:
                        k["grade"] = grade
            continue

        elif i["countType"] == "FCES" and i["count"] > 1.0:
            for j in i["requisiteItems"]:
                j["grade"] = i["count"]

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
            p["groups"].append(
                build_dict(
                    courses[i]["type"],
                    courses[i]["requisiteItems"],
                    courses,
                    courses[i]["countType"],
                )
            )
        return (p, manual_review)

    elif len(roots) == 1:
        p = build_dict(
            courses[type + "1"]["type"],
            courses[type + "1"]["requisiteItems"],
            courses,
            courses[type + "1"]["countType"],
        )
        return (p, manual_review)

    else:
        print("Empty")
        return ({}, manual_review)


def build_dict(
    log_str: str, requisite_items: list[dict], courses: dict[str, dict], countType: str
):
    p = {"logic": eval_log_str(log_str), "groups": []}

    if countType == "FCES" and p["logic"] == "OR":
        requisite_items = return_fce_groups(requisite_items)

    for i in requisite_items:
        if type(i) == tuple:
            p["groups"].append(
                build_dict(invert_log_str(log_str), i, courses, countType)
            )

        else:
            if i["courseEntity"]:
                try:
                    p["groups"].append((i["code"], i["grade"]))
                except KeyError:
                    p["groups"].append((i["code"], 50))

            elif not i["courseEntity"] and len(i["code"]) == 2:
                p["groups"].append(
                    build_dict(
                        courses[i["code"]]["type"],
                        courses[i["code"]]["requisiteItems"],
                        courses,
                        "",
                    )
                )

            else:
                p["groups"].append((i["display"], i.get("grade")))

    return p


def return_fce_groups(courses: list):
    course_suffixes = {
        0.5: [course for course in courses if course.get("code", "")[6:7] == "H"],
        1.0: [course for course in courses if course.get("code", "")[6:7] == "Y"],
        0.0: [course for course in courses if course.get("code", "")[6:7] not in "HY"],
    }
    if course_suffixes[0.5] != [] and course_suffixes[1.0] != []:
        return (
            list(itertools.combinations(course_suffixes[0.5], 2))
            + course_suffixes[1.0]
            + course_suffixes[0.0]
        )

    else:
        return courses


def eval_log_str(log_str: str):
    return "OR" if log_str == "MINIMUM" or log_str == "ANY" else "AND"


def invert_log_str(op: str):
    return "OR" if op == "AND" else "AND"

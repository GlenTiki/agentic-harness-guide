#!/usr/bin/env python3
"""Validate a starter-kit plan against kit-manifest.json and list what the plan writes and what the person runs.

Usage: python3 -I validate_plan.py PLAN.json [--manifest PATH] [--render]
Exit 0: the plan is valid. Exit 1: the plan is invalid. Exit 2: the plan or the manifest cannot be read.
"""

import argparse
import json
import pathlib
import re
import sys

HERE = pathlib.Path(__file__).resolve().parent
PLACEHOLDER = re.compile(r"\{\{([a-z_]+)\}\}")
JSON_PLACEHOLDER = re.compile(r'"\{\{([a-z_]+)\}\}"')
UNSET_TEXT = "not set yet"


def is_set(value):
    return value is not None and value != "" and value != [] and value is not False


def holds(condition, answers):
    value = answers.get(condition["answer"])
    if "includes" in condition:
        return isinstance(value, list) and condition["includes"] in value
    if "equals" in condition:
        return value == condition["equals"]
    if "is_set" in condition:
        return is_set(value) == condition["is_set"]
    raise ValueError(f"unknown condition: {condition}")


def all_hold(conditions, answers):
    return all(holds(condition, answers) for condition in conditions)


def outcome_holds(then, answers):
    if "require" in then:
        return is_set(answers.get(then["require"]))
    if "forbid" in then:
        return not holds(then["forbid"], answers)
    return holds(then, answers)


def check_choice(question, value, values):
    qid = question["id"]
    if question["type"] == "single":
        if not isinstance(value, str):
            return [(f"{qid}-type", f"{qid} must be one value.")]
        return [] if value in values else [(f"{qid}-option", f"{qid} has no option {value!r}.")]
    if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
        return [(f"{qid}-type", f"{qid} must be a list of values.")]
    errors = [(f"{qid}-option", f"{qid} has no option {item!r}.") for item in value if item not in values]
    if len(set(value)) != len(value):
        errors.append((f"{qid}-duplicate", f"{qid} lists a value twice."))
    if len(value) < question.get("min", 0):
        errors.append((f"{qid}-min", f"{qid} needs at least {question['min']} value(s)."))
    if len(value) > question.get("max", len(values)):
        errors.append((f"{qid}-max", f"{qid} allows at most {question['max']} value(s)."))
    return errors


def check_string(question, value):
    qid = question["id"]
    if not isinstance(value, str):
        return [(f"{qid}-type", f"{qid} must be text.")]
    if len(value) < question.get("min", 0):
        return [(f"{qid}-min", f"{qid} is shorter than {question['min']} character(s). Leave it out instead.")]
    if len(value) > question.get("max", len(value)):
        return [(f"{qid}-max", f"{qid} is longer than {question['max']} characters.")]
    if "pattern" in question and not re.fullmatch(question["pattern"], value):
        return [(
            f"{qid}-pattern",
            f"{qid} must hold a command and no shell operator (; & | ` $ < >), quote, backslash, "
            "bracket ( ) [ ] { }, wildcard (* ?) or control character such as a tab.",
        )]
    return []


def check_answer(question, value):
    if value is None:
        return []
    if question["type"] == "boolean":
        return [] if isinstance(value, bool) else [(f"{question['id']}-type", f"{question['id']} must be true or false.")]
    if question["type"] == "string":
        return check_string(question, value)
    return check_choice(question, value, [option["value"] for option in question["options"]])


def with_defaults(manifest, given):
    return {question["id"]: given.get(question["id"], question.get("default")) for question in manifest["questions"]}


def validate(plan, manifest):
    """Return (errors, warnings, answers). Each error and warning is a (rule id, message) pair."""
    if not isinstance(plan, dict) or not isinstance(plan.get("answers"), dict):
        return [("plan-shape", 'The plan must be an object with an "answers" object.')], [], {}
    known = {question["id"] for question in manifest["questions"]}
    errors = [(f"{key}-unknown", f"{key} is not a question in this kit.") for key in plan["answers"] if key not in known]
    answers = with_defaults(manifest, plan["answers"])
    for question in manifest["questions"]:
        errors += check_answer(question, answers[question["id"]])
    if errors:
        return errors, [], answers
    warnings = []
    for rule in manifest["rules"]:
        if all_hold(rule["when"], answers) and not outcome_holds(rule["then"], answers):
            (warnings if rule["level"] == "warning" else errors).append((rule["id"], rule["message"]))
    return errors, warnings, answers


def resolve(answers, manifest):
    """Return the writes, the commands for the person, and the skills the person chooses outside the kit."""
    items = [item for item in manifest["items"] if all_hold(item["when"], answers)]
    skills = next(question for question in manifest["questions"] if question["id"] == "skills")
    to_find = [option for option in skills["options"] if option["value"] in (answers.get("skills") or [])]
    return {
        "items": [item["id"] for item in items],
        "writes": [{"item": item["id"], **write} for item in items for write in item["writes"]],
        "run": [{"item": item["id"], **step} for item in items for step in item["run"]],
        "skills_to_find": [option["value"] for option in to_find if not option["ships"]],
    }


def render(text, answers, as_json):
    if not as_json:
        return PLACEHOLDER.sub(lambda match: answers.get(match.group(1)) or UNSET_TEXT, text)
    text = JSON_PLACEHOLDER.sub(lambda match: json.dumps(answers.get(match.group(1))), text)
    return PLACEHOLDER.sub(lambda match: json.dumps(answers.get(match.group(1)) or UNSET_TEXT)[1:-1], text)


def print_resolution(resolution, answers, render_files, kit_dir):
    for write in resolution["writes"]:
        print(f"write {write['path']} ({write['mode']}) from {write['source']} [item {write['item']}]")
        if render_files:
            source = (kit_dir / write["source"]).read_text()
            print(render(source, answers, write["source"].endswith(".json")))
    for step in resolution["run"]:
        print(f"person runs: {step['command']} ({step['why']}) [item {step['item']}]")
    for skill in resolution["skills_to_find"]:
        print(f"person chooses a skill: {skill}")


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("plan")
    parser.add_argument("--manifest", default=str(HERE / "kit-manifest.json"))
    parser.add_argument("--render", action="store_true", help="print each file as it would be written")
    args = parser.parse_args(argv)
    try:
        manifest = json.loads(pathlib.Path(args.manifest).read_text())
        plan = json.loads(pathlib.Path(args.plan).read_text())
    except (OSError, ValueError) as error:
        print(f"read-error: {error}", file=sys.stderr)
        return 2
    errors, warnings, answers = validate(plan, manifest)
    for rule_id, message in warnings:
        print(f"warning: {rule_id}: {message}")
    for rule_id, message in errors:
        print(f"{rule_id}: {message}")
    if errors:
        return 1
    print_resolution(resolve(answers, manifest), answers, args.render, pathlib.Path(args.manifest).resolve().parent)
    return 0


if __name__ == "__main__":
    sys.exit(main())

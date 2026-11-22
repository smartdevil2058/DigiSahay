<<<<<<< HEAD
from datetime import date
from flask import json,jsonify
def get_next_qualifying_date(today=None):

    if today is None:
        today = date.today()

    qualifying_dates = [
        (1, 1),
        (4, 1),
        (7, 1),
        (10, 1)
    ]

    for month, day in qualifying_dates:
        qualifying_date = date(today.year, month, day)

        if qualifying_date >= today:
            return qualifying_date

    return date(today.year + 1, 1, 1)


def calculate_age(dob, reference_date):

    age = reference_date.year - dob.year

    if (reference_date.month, reference_date.day) < (
        dob.month, dob.day
    ):
        age -= 1

    return age


def parse_outcome(outcome):

    if not outcome:
        return "UNKNOWN", "No outcome configured"

    if ":" in outcome:
        action, message = outcome.split(":", 1)
        return action.strip(), message.strip()

    return outcome.strip(), ""


def evaluate_rule(rule, answers, today):

    try:
        config = json.loads(rule.condition_config or "{}")

    except json.JSONDecodeError:
        return {
            "status": "INVALID_RULE",
            "message": "Invalid condition configuration"
        }

    condition_type = rule.condition_type

    # BOOLEAN_EQUAL rules
    if condition_type == "BOOLEAN_EQUAL":

        field = config.get("field")
        expected = config.get("expected")

        if not field or field not in answers:
            return {
                "status": "INCOMPLETE",
                "message": f"Missing answer: {field}"
            }

        actual = answers[field]

        if not isinstance(actual, bool):
            return {
                "status": "INVALID_ANSWER",
                "message": f"{field} must be true or false"
            }

        passed = actual == expected

    # AGE_COMPARE rule
    elif condition_type == "AGE_COMPARE":

        # The current workbook rule does not specify
        # a field, so we use date_of_birth.
        dob_value = answers.get("date_of_birth")

        if not dob_value:
            return {
                "status": "INCOMPLETE",
                "message": "Missing answer: date_of_birth"
            }

        try:
            dob = date.fromisoformat(dob_value)

        except (ValueError, TypeError):
            return {
                "status": "INVALID_ANSWER",
                "message": "Date of birth must use YYYY-MM-DD format"
            }

        if dob > today:
            return {
                "status": "INVALID_ANSWER",
                "message": "Date of birth cannot be in the future"
            }

        reference_date = get_next_qualifying_date(today)

        age = calculate_age(dob, reference_date)

        target_age = config.get("target_age")
        operator = config.get("operator")

        if not isinstance(target_age, int):
            return {
                "status": "INVALID_RULE",
                "message": "Invalid target age configuration"
            }

        if operator == ">=":
            passed = age >= target_age
        elif operator == ">":
            passed = age > target_age
        elif operator == "<=":
            passed = age <= target_age
        elif operator == "<":
            passed = age < target_age
        elif operator == "==":
            passed = age == target_age
        else:
            return {
                "status": "INVALID_RULE",
                "message": "Unsupported age comparison operator"
            }

    else:
        return {
            "status": "INVALID_RULE",
            "message": f"Unsupported condition type: {condition_type}"
        }

    outcome = (
        rule.outcome_if_true if passed
        else rule.outcome_if_false
    )

    action, message = parse_outcome(outcome)

    return {
        "status": action,
        "message": message,
        "passed": passed
    }

=======
from datetime import date
from flask import json,jsonify
def get_next_qualifying_date(today=None):

    if today is None:
        today = date.today()

    qualifying_dates = [
        (1, 1),
        (4, 1),
        (7, 1),
        (10, 1)
    ]

    for month, day in qualifying_dates:
        qualifying_date = date(today.year, month, day)

        if qualifying_date >= today:
            return qualifying_date

    return date(today.year + 1, 1, 1)


def calculate_age(dob, reference_date):

    age = reference_date.year - dob.year

    if (reference_date.month, reference_date.day) < (
        dob.month, dob.day
    ):
        age -= 1

    return age


def parse_outcome(outcome):

    if not outcome:
        return "UNKNOWN", "No outcome configured"

    if ":" in outcome:
        action, message = outcome.split(":", 1)
        return action.strip(), message.strip()

    return outcome.strip(), ""


def evaluate_rule(rule, answers, today):

    try:
        config = json.loads(rule.condition_config or "{}")

    except json.JSONDecodeError:
        return {
            "status": "INVALID_RULE",
            "message": "Invalid condition configuration"
        }

    condition_type = rule.condition_type

    # BOOLEAN_EQUAL rules
    if condition_type == "BOOLEAN_EQUAL":

        field = config.get("field")
        expected = config.get("expected")

        if not field or field not in answers:
            return {
                "status": "INCOMPLETE",
                "message": f"Missing answer: {field}"
            }

        actual = answers[field]

        if not isinstance(actual, bool):
            return {
                "status": "INVALID_ANSWER",
                "message": f"{field} must be true or false"
            }

        passed = actual == expected

    # AGE_COMPARE rule
    elif condition_type == "AGE_COMPARE":

        # The current workbook rule does not specify
        # a field, so we use date_of_birth.
        dob_value = answers.get("date_of_birth")

        if not dob_value:
            return {
                "status": "INCOMPLETE",
                "message": "Missing answer: date_of_birth"
            }

        try:
            dob = date.fromisoformat(dob_value)

        except (ValueError, TypeError):
            return {
                "status": "INVALID_ANSWER",
                "message": "Date of birth must use YYYY-MM-DD format"
            }

        if dob > today:
            return {
                "status": "INVALID_ANSWER",
                "message": "Date of birth cannot be in the future"
            }

        reference_date = get_next_qualifying_date(today)

        age = calculate_age(dob, reference_date)

        target_age = config.get("target_age")
        operator = config.get("operator")

        if not isinstance(target_age, int):
            return {
                "status": "INVALID_RULE",
                "message": "Invalid target age configuration"
            }

        if operator == ">=":
            passed = age >= target_age
        elif operator == ">":
            passed = age > target_age
        elif operator == "<=":
            passed = age <= target_age
        elif operator == "<":
            passed = age < target_age
        elif operator == "==":
            passed = age == target_age
        else:
            return {
                "status": "INVALID_RULE",
                "message": "Unsupported age comparison operator"
            }

    else:
        return {
            "status": "INVALID_RULE",
            "message": f"Unsupported condition type: {condition_type}"
        }

    outcome = (
        rule.outcome_if_true if passed
        else rule.outcome_if_false
    )

    action, message = parse_outcome(outcome)

    return {
        "status": action,
        "message": message,
        "passed": passed
    }

>>>>>>> c981506dbd2f314e63b7e90f4ab444ee1eca2d2c

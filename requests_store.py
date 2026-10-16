import json
import os

VALID_CARD_TYPES = ("visitor", "student", "staff")
VALID_STATUSES = ("requested", "approved", "issued", "returned")
NEXT_STATUS = {"requested": "approved", "approved": "issued", "issued": "returned"}
REQUIRED_KEYS = ("id", "fellow_id", "card_type", "status", "approved_by")
ASCII_DIGITS = "0123456789"

_requests = {}


def validate_fellow_id(fellow_id):
    """Raise ValueError if fellow_id is not a non-blank piece of text."""
    if not isinstance(fellow_id, str):
        raise ValueError("fellow_id must be text")
    if fellow_id.strip() == "":
        raise ValueError("fellow_id cannot be blank")


def validate_card_type(card_type):
    """Raise ValueError if card_type is not visitor, student or staff."""
    if not isinstance(card_type, str):
        raise ValueError("card_type must be text")
    if card_type not in VALID_CARD_TYPES:
        raise ValueError("card_type must be visitor, student or staff")


def validate_request_id(request_id):
    """Raise ValueError if request_id does not look like A001."""
    if not isinstance(request_id, str):
        raise ValueError("request_id must be text")
    if len(request_id) < 4 or request_id[0] != "A":
        raise ValueError("request_id must look like A001")
    digits = request_id[1:]
    for character in digits:
        if character not in ASCII_DIGITS:
            raise ValueError("request_id must look like A001")
    number = int(digits)
    if number == 0 or request_id != "A" + str(number).zfill(3):
        raise ValueError("request_id must look like A001")


def _next_id():
    """Work out the next free ID, like A001, A002, A003."""
    highest = 0
    for request_id in _requests:
        number = int(request_id[1:])
        if number > highest:
            highest = number
    return "A" + str(highest + 1).zfill(3)


def create_request(fellow_id, card_type):
    """Make a new request and return a copy of it."""
    validate_fellow_id(fellow_id)
    validate_card_type(card_type)

    request_id = _next_id()
    request = {
        "id": request_id,
        "fellow_id": fellow_id.strip(),
        "card_type": card_type,
        "status": "requested",
        "approved_by": None,
    }
    _requests[request_id] = request

    return dict(request)


def get_request(request_id):
    """Return a copy of one request. Raise ValueError if it is bad or unknown."""
    validate_request_id(request_id)
    if request_id not in _requests:
        raise ValueError("request id not found")
    return dict(_requests[request_id])


def list_requests():
    """Return a list of copies of all requests, in ID order (A001, A002, ...)."""
    all_requests = list(_requests.values())
    all_requests.sort(key=lambda request: int(request["id"][1:]))
    return [dict(request) for request in all_requests]


def update_request(request_id, status, approved_by=None):
    """Move a request to its next status and return a copy.

    Every check happens before anything is written, so a rejected
    update leaves the stored record exactly as it was.
    """
    validate_request_id(request_id)
    if request_id not in _requests:
        raise ValueError("request id not found")
    if not isinstance(status, str) or status not in VALID_STATUSES:
        raise ValueError("invalid status")

    current = _requests[request_id]
    if NEXT_STATUS.get(current["status"]) != status:
        raise ValueError("cannot move from " + current["status"] + " to " + status)

    if status == "approved":
        if not isinstance(approved_by, str) or approved_by.strip() == "":
            raise ValueError("approved_by cannot be blank")
        new_approver = approved_by.strip()
    else:
        if approved_by is not None:
            raise ValueError("approved_by can only be set when approving")
        new_approver = current["approved_by"]

    current["status"] = status
    current["approved_by"] = new_approver
    return dict(current)


def _validate_record(record):
    """Raise ValueError if one request loaded from a file is not valid."""
    if not isinstance(record, dict):
        raise ValueError("each request must be an object")
    if set(record.keys()) != set(REQUIRED_KEYS):
        raise ValueError("each request must have exactly the keys: " + ", ".join(REQUIRED_KEYS))

    validate_request_id(record["id"])
    validate_fellow_id(record["fellow_id"])
    validate_card_type(record["card_type"])

    if record["status"] not in VALID_STATUSES:
        raise ValueError("invalid status: " + str(record["status"]))

    approved_by = record["approved_by"]
    if record["status"] == "requested":
        if approved_by is not None:
            raise ValueError("a requested request cannot have approved_by")
    else:
        if not isinstance(approved_by, str) or approved_by.strip() == "":
            raise ValueError("approved_by is required once a request is approved")


def save_requests(path):
    """Save all requests to a JSON file without damaging an existing good file."""
    temp_path = path + ".tmp"
    data = [dict(_requests[key]) for key in sorted(_requests)]
    try:
        with open(temp_path, "w", encoding="utf-8") as file:
            json.dump(data, file, indent=2)
        os.replace(temp_path, path)
    except Exception:
        if os.path.exists(temp_path):
            os.remove(temp_path)
        raise


def load_requests(path):
    """Load requests from a JSON file.

    Raise FileNotFoundError if the file does not exist and ValueError
    if the file is bad. Existing data is only replaced when the whole
    file is valid.
    """
    with open(path, "r", encoding="utf-8") as file:
        try:
            data = json.load(file)
        except json.JSONDecodeError:
            raise ValueError("file is not valid JSON")

    if not isinstance(data, list):
        raise ValueError("file must contain a list of requests")

    loaded = {}
    for record in data:
        _validate_record(record)
        if record["id"] in loaded:
            raise ValueError("duplicate id in file: " + record["id"])
        loaded[record["id"]] = dict(record)

    _requests.clear()
    _requests.update(loaded)

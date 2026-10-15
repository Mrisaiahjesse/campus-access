VALID_CARD_TYPES = ("visitor", "student", "staff")

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
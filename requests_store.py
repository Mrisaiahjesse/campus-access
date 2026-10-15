# Engineer A owns this file.

VALID_CARD_TYPES = ("visitor", "student", "staff")

# The "filing cabinet": request id -> request dictionary
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
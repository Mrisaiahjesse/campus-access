from requests_store import get_request, update_request


def approve_request(request_id, approved_by):
    """Approve a requested request. Reject anything else and change nothing."""
    request = get_request(request_id)

    if not isinstance(approved_by, str):
        raise ValueError("approved_by must be text")
    if approved_by.strip() == "":
        raise ValueError("approved_by cannot be blank")

    if request["status"] != "requested":
        raise ValueError("Only a requested request can be approved")

    update_request(request_id, "approved", approved_by.strip())
    return get_request(request_id)


def issue_card(request_id):
    """Issue a card for an approved request. Reject anything else."""
    request = get_request(request_id)

    if request["status"] != "approved":
        raise ValueError("Only an approved request can be issued")
    if not request["approved_by"] or request["approved_by"].strip() == "":
        raise ValueError("Cannot issue a card without an approver")

    update_request(request_id, "issued", request["approved_by"])
    return get_request(request_id)


def return_card(request_id):
    """Return an issued card. Reject anything else. Returned is final."""
    request = get_request(request_id)

    if request["status"] != "issued":
        raise ValueError("Only an issued card can be returned")

    update_request(request_id, "returned", request["approved_by"])
    return get_request(request_id)
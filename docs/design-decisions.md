# Design Decisions

## 1. What does one request dictionary look like?
```python
{
    "id": "A001",
    "fellow_id": "F001",
    "card_type": "visitor",
    "status": "requested",
    "approved_by": None,
}
```
A dictionary is used because requests are found by their ID. All requests live in one dictionary, `{"A001": {...}, "A002": {...}}`, so a lookup is quick and an ID can only appear once. `approved_by` is `None` (saved as `null` in JSON) until the request is approved.

## 2. What should create_request return?
A copy of the new request dictionary. A copy means the caller cannot change the stored record by accident. The stored record only changes through our own functions.

## 3. How will functions report invalid inputs?
They raise `ValueError` with a clear message. The menu catches it and shows the message to the user. Loading a file that does not exist raises `FileNotFoundError`, and the menu handles that separately, for example on the first run.

## 4. Where is the next ID generated?
In `_next_id()` in `requests_store.py`. It finds the highest number among the IDs already stored and adds 1, so there is no separate counter to forget. After a reload from JSON, the next ID continues correctly (A002, not A001).

## 5. How will Engineer B call Engineer A's storage functions?
Engineer B never edits records directly. She calls these functions from `requests_store.py`:

| Function | Purpose |
|---|---|
| `create_request(fellow_id, card_type)` | Create a new request |
| `get_request(request_id)` | Read one request (returns a copy) |
| `list_requests()` | Read all requests, sorted by ID (returns copies) |
| `update_request(request_id, status, approved_by=None)` | Move a request to its next status |
| `save_requests(path)` / `load_requests(path)` | Save and load the JSON file |

`update_request` only allows the next legal step: requested -> approved -> issued -> returned. Approving needs a non-blank approver.

## 6. What happens if a saved JSON file is invalid?
`load_requests` checks the whole file before it changes anything. It rejects broken JSON, an empty file, something that is not a list, missing or extra keys, duplicate IDs, invalid statuses and a missing approver. The existing data in memory is only replaced after the whole file passes, so a bad file never wipes valid data. The file is never silently replaced with empty data.

## 7. Which data must never change on a rejected operation?
Every stored request: `id`, `fellow_id`, `card_type`, `status` and `approved_by`. All checks run before anything is written, so a rejected create, update or load leaves the stored data as it was. A failed save also leaves the old file safe, because it writes to a temporary file first. Tests compare the record before and after a rejected action.
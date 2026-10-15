# Campus Access

Campus Access is a Python command-line app that manages campus access-card requests. A request is created, approved by a staff identifier, issued and finally returned. Invalid actions are rejected, and data is saved to JSON so it survives a restart.

## Team
- Engineer A: (your full name) - creating and validating requests, unique IDs, saving and loading
- Engineer B: (partner's full name) - approve, issue and return workflow, and the menu

## How a request moves
requested -> approved -> issued -> returned

No steps can be skipped, and "returned" is final. Only a request with a non-empty approver can be issued.

## Request fields
- `id` (A001, A002, ...)
- `fellow_id`
- `card_type` (visitor, student or staff)
- `status`
- `approved_by`

## Project files
- `main.py` - starts the app
- `requests_store.py` - Engineer A: create, find, save and load requests
- `workflow.py` - Engineer B: approve, issue and return
- `cli.py` - Engineer B: the command-line menu
- `tests/` - unittest tests
- `docs/design-decisions.md` - how we agreed to build it
- `docs/ai-learning-log.md` - what we learned with AI and how we checked it

## How to run
```
python3 main.py
```

## How to run the tests
```
python3 -m unittest discover -s tests -v
```

## Rules we follow
- Python standard library only
- Input is checked before any data is changed
- A failed action leaves the record exactly as it was
- A bad JSON file is rejected with a clear error and never replaced with empty data
- Work goes through branches and pull requests, reviewed by the other engineer

## Status
(Update this at the end, for example: "All 8 challenge-board cases demonstrated. Final commit: ...")
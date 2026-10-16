from requests_store import (
    create_request,
    get_request,
    list_requests,
    save_requests,
    load_requests,
)
from workflow import approve_request, issue_card, return_card

DATA_FILE = "requests.json"

MENU = """
===== Campus Access =====
1. Create request
2. View request
3. Approve request
4. Issue card
5. Return card
6. List requests
7. Save to file
8. Load from file
9. Quit
"""


def show_request(request):
    """Print one request in a readable way."""
    print("  ID:         ", request["id"])
    print("  Fellow ID:  ", request["fellow_id"])
    print("  Card type:  ", request["card_type"])
    print("  Status:     ", request["status"])
    print("  Approved by:", request["approved_by"])


def run_menu():
    """Show the menu again and again until the user chooses Quit."""
    while True:
        print(MENU)
        choice = input("Choose an option (1-9): ").strip()

        try:
            if choice == "1":
                fellow_id = input("Fellow ID: ")
                card_type = input("Card type (visitor/student/staff): ").strip().lower()
                show_request(create_request(fellow_id, card_type))

            elif choice == "2":
                request_id = input("Request ID (e.g. A001): ").strip().upper()
                show_request(get_request(request_id))

            elif choice == "3":
                request_id = input("Request ID: ").strip().upper()
                approver = input("Approver ID (e.g. M01): ")
                show_request(approve_request(request_id, approver))
                print("Approved.")

            elif choice == "4":
                request_id = input("Request ID: ").strip().upper()
                show_request(issue_card(request_id))
                print("Card issued.")

            elif choice == "5":
                request_id = input("Request ID: ").strip().upper()
                show_request(return_card(request_id))
                print("Card returned.")

            elif choice == "6":
                requests = list_requests()
                if not requests:
                    print("No requests yet.")
                for request in requests:
                    show_request(request)
                    print("  ---")

            elif choice == "7":
                save_requests(DATA_FILE)
                print("Saved to", DATA_FILE)

            elif choice == "8":
                load_requests(DATA_FILE)
                print("Loaded from", DATA_FILE)

            elif choice == "9":
                answer = input("Save before quitting? (y/n): ").strip().lower()
                if answer == "y":
                    save_requests(DATA_FILE)
                    print("Saved to", DATA_FILE)
                print("Goodbye.")
                break

            else:
                print("Invalid option. Please type a number from 1 to 9.")

        except ValueError as error:
            print("Rejected:", error)
        except FileNotFoundError:
            print("File not found. Save first, then load.")
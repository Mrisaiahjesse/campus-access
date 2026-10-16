import unittest

import requests_store
from workflow import approve_request, issue_card, return_card


class TestWorkflow(unittest.TestCase):

    def setUp(self):
        requests_store._requests.clear()
        self.request = requests_store.create_request("F001", "visitor")
        self.request_id = self.request["id"]

    def test_issue_before_approval_is_rejected(self):
        before = requests_store.get_request(self.request_id)
        with self.assertRaises(ValueError):
            issue_card(self.request_id)
        after = requests_store.get_request(self.request_id)
        self.assertEqual(before, after)
        self.assertEqual(after["status"], "requested")

    def test_blank_approver_is_rejected(self):
        before = requests_store.get_request(self.request_id)
        with self.assertRaises(ValueError):
            approve_request(self.request_id, "   ")
        after = requests_store.get_request(self.request_id)
        self.assertEqual(before, after)
        self.assertEqual(after["status"], "requested")

    def test_full_workflow(self):
        approved = approve_request(self.request_id, "M01")
        self.assertEqual(approved["status"], "approved")
        self.assertEqual(approved["approved_by"], "M01")

        issued = issue_card(self.request_id)
        self.assertEqual(issued["status"], "issued")

        returned = return_card(self.request_id)
        self.assertEqual(returned["status"], "returned")

    def test_double_return_and_issue_after_return_are_rejected(self):
        approve_request(self.request_id, "M01")
        issue_card(self.request_id)
        return_card(self.request_id)

        before = requests_store.get_request(self.request_id)
        with self.assertRaises(ValueError):
            return_card(self.request_id)
        with self.assertRaises(ValueError):
            issue_card(self.request_id)
        after = requests_store.get_request(self.request_id)

        self.assertEqual(before, after)
        self.assertEqual(after["status"], "returned")


if __name__ == "__main__":
    unittest.main()
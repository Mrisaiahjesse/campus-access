import json
import os
import tempfile
import unittest
from unittest import mock

import requests_store


class TestRequestsStore(unittest.TestCase):

    def setUp(self):
        requests_store._requests.clear()
        self.temp_dir = tempfile.TemporaryDirectory()
        self.path = os.path.join(self.temp_dir.name, "requests.json")

    def tearDown(self):
        self.temp_dir.cleanup()
        requests_store._requests.clear()

    def write_json(self, data):
        with open(self.path, "w", encoding="utf-8") as file:
            json.dump(data, file)

    def test_create_valid_request(self):
        request = requests_store.create_request("F001", "visitor")
        self.assertEqual(request, {
            "id": "A001",
            "fellow_id": "F001",
            "card_type": "visitor",
            "status": "requested",
            "approved_by": None,
        })

    def test_invalid_card_type_rejected(self):
        with self.assertRaises(ValueError):
            requests_store.create_request("F001", "vip")
        self.assertEqual(len(requests_store._requests), 0)

    def test_blank_fellow_id_rejected(self):
        with self.assertRaises(ValueError):
            requests_store.create_request("   ", "visitor")
        self.assertEqual(len(requests_store._requests), 0)

    def test_non_ascii_digits_rejected(self):
        requests_store.create_request("F001", "visitor")
        with self.assertRaises(ValueError):
            requests_store.get_request("A\u0661\u0662\u0663")

    def test_a000_and_padded_ids_rejected(self):
        requests_store.create_request("F001", "visitor")
        for bad_id in ["A000", "A0001"]:
            with self.assertRaises(ValueError):
                requests_store.get_request(bad_id)

    def test_get_request_returns_copy(self):
        requests_store.create_request("F001", "visitor")
        copy = requests_store.get_request("A001")
        copy["status"] = "issued"
        self.assertEqual(requests_store.get_request("A001")["status"], "requested")

    def test_new_id_after_reload(self):
        requests_store.create_request("F001", "visitor")
        requests_store.save_requests(self.path)
        requests_store._requests.clear()
        requests_store.load_requests(self.path)
        new_request = requests_store.create_request("F002", "staff")
        self.assertEqual(new_request["id"], "A002")

    def test_corrupted_json_rejected_and_data_kept(self):
        requests_store.create_request("F001", "visitor")
        with open(self.path, "w", encoding="utf-8") as file:
            file.write("{ this is not json")
        with self.assertRaises(ValueError):
            requests_store.load_requests(self.path)
        self.assertEqual(len(requests_store._requests), 1)

    def test_missing_file_raises_and_data_kept(self):
        requests_store.create_request("F001", "visitor")
        with self.assertRaises(FileNotFoundError):
            requests_store.load_requests(self.path)
        self.assertEqual(len(requests_store._requests), 1)

    def test_duplicate_ids_rejected(self):
        record = {
            "id": "A001",
            "fellow_id": "F001",
            "card_type": "visitor",
            "status": "requested",
            "approved_by": None,
        }
        self.write_json([record, dict(record)])
        with self.assertRaises(ValueError):
            requests_store.load_requests(self.path)

    def test_missing_keys_rejected(self):
        self.write_json([{"id": "A001", "fellow_id": "F001"}])
        with self.assertRaises(ValueError):
            requests_store.load_requests(self.path)

    def test_failed_save_keeps_old_file(self):
        requests_store.create_request("F001", "visitor")
        requests_store.save_requests(self.path)
        with open(self.path, "r", encoding="utf-8") as file:
            before = file.read()

        requests_store.create_request("F002", "staff")
        with mock.patch("requests_store.json.dump", side_effect=OSError("disk full")):
            with self.assertRaises(OSError):
                requests_store.save_requests(self.path)

        with open(self.path, "r", encoding="utf-8") as file:
            after = file.read()
        self.assertEqual(before, after)
        self.assertFalse(os.path.exists(self.path + ".tmp"))

    def test_update_request_full_workflow(self):
        requests_store.create_request("F001", "visitor")
        requests_store.update_request("A001", "approved", "M01")
        requests_store.update_request("A001", "issued")
        result = requests_store.update_request("A001", "returned")
        self.assertEqual(result["status"], "returned")
        self.assertEqual(result["approved_by"], "M01")

    def test_update_request_illegal_transition_keeps_record(self):
        requests_store.create_request("F001", "visitor")
        before = requests_store.get_request("A001")
        with self.assertRaises(ValueError):
            requests_store.update_request("A001", "issued")
        self.assertEqual(requests_store.get_request("A001"), before)

    def test_update_request_blank_approver_keeps_record(self):
        requests_store.create_request("F001", "visitor")
        before = requests_store.get_request("A001")
        with self.assertRaises(ValueError):
            requests_store.update_request("A001", "approved", "   ")
        self.assertEqual(requests_store.get_request("A001"), before)

    def test_list_requests_empty(self):
        self.assertEqual(requests_store.list_requests(), [])

    def test_list_requests_in_id_order(self):
        requests_store.create_request("F001", "visitor")
        requests_store.create_request("F002", "staff")
        requests_store.create_request("F003", "student")
        ids = [request["id"] for request in requests_store.list_requests()]
        self.assertEqual(ids, ["A001", "A002", "A003"])

    def test_list_requests_returns_copies(self):
        requests_store.create_request("F001", "visitor")
        result = requests_store.list_requests()
        result[0]["status"] = "issued"
        self.assertEqual(requests_store.get_request("A001")["status"], "requested")

    def test_list_requests_shows_updated_status(self):
        requests_store.create_request("F001", "visitor")
        requests_store.update_request("A001", "approved", "M01")
        result = requests_store.list_requests()
        self.assertEqual(result[0]["status"], "approved")
        self.assertEqual(result[0]["approved_by"], "M01")


if __name__ == "__main__":
    unittest.main()
import json
import os
import tempfile
import unittest

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


if __name__ == "__main__":
    unittest.main()
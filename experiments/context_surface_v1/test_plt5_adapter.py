import unittest

from plt5_adapter import bounded_input, check_request, checked_target
from prototype import digest


class AdapterContractTests(unittest.TestCase):
    def test_token_budget_keeps_near_cursor_and_mask(self):
        ids, truncated = bounded_input([11, 12, 13, 99, 1], 99, 1, limit=4)
        self.assertEqual(ids, [12, 13, 99, 1])
        self.assertTrue(truncated)

    def test_budget_does_not_add_or_remove_short_context(self):
        self.assertEqual(bounded_input([11, 99, 1], 99, 1, limit=4),
                         ([11, 99, 1], False))

    def test_missing_mask_or_unsafe_budget_rejected(self):
        with self.assertRaises(ValueError):
            bounded_input([11, 99], 99, 1)
        with self.assertRaises(ValueError):
            bounded_input([11, 99, 1], 99, 1, limit=2)

    def test_multitoken_variant_allowed_unknown_or_injected_mask_rejected(self):
        self.assertEqual(checked_target([99, 11, 12, 98], 99, 98, 2), [99, 11, 12, 98])
        for ids in ([99, 2, 98], [99, 98], [99, 99, 98], [11, 12, 98]):
            with self.assertRaises(ValueError):
                checked_target(ids, 99, 98, 2)

    def test_tampered_context_rejected(self):
        payload = {"schemaVersion": 1, "requests": [{"context": {"text": "miasto "}}]}
        request = {**payload, "requestSha256": digest(payload)}
        check_request(request)
        request["requests"][0]["context"]["text"] = "statek "
        with self.assertRaises(ValueError):
            check_request(request)

    def test_gold_even_with_matching_hash_rejected(self):
        payload = {"schemaVersion": 1, "requests": [{"expected": "Łódź"}]}
        with self.assertRaises(ValueError):
            check_request({**payload, "requestSha256": digest(payload)})


if __name__ == "__main__":
    unittest.main()

"""Acceptance/regression checks for the offline experiment, not AI quality tests."""
import copy
import json
import math
from pathlib import Path
import unittest

from prototype import (candidate_groups, canonical_bytes, context_window, digest,
                       evaluate, load_sidecar, prepare, resolve, validate_predictions,
                       word_spans)

HERE = Path(__file__).parent


class ContextTests(unittest.TestCase):
    def test_case_diacritics_punctuation_and_newlines_are_exact(self):
        original = "W Łodzi jest zimno.\nPytam: czy łódź dopłynie? "
        window = context_window(original)
        self.assertEqual(window.text, original)
        self.assertEqual(window.word_count, 8)
        self.assertFalse(window.character_truncated)
        self.assertFalse(window.word_truncated)
        self.assertIn(original.index("\n"), window.boundary_cues)

    def test_long_history_keeps_the_disambiguating_previous_sentence(self):
        city = "Rozmawiamy o polskich miastach. W tym przykładzie jest to "
        boat = "Oglądamy drewniane jednostki pływające. W tym przykładzie jest to "
        self.assertEqual(context_window(city, 2).text, context_window(boat, 2).text)
        self.assertNotEqual(context_window(city).text, context_window(boat).text)
        self.assertIn("miastach.", context_window(city).text)

    def test_word_budget_keeps_exact_complete_suffix(self):
        value = " ".join("słowo" + str(i) for i in range(90)) + " "
        window = context_window(value)
        self.assertEqual(window.word_count, 64)
        self.assertTrue(window.word_truncated)
        self.assertTrue(value.endswith(window.text))

    def test_character_budget_does_not_keep_a_cut_word(self):
        window = context_window("pierwsze drugie końcowe ", max_chars=17)
        self.assertEqual(window.text, " drugie końcowe ")
        self.assertLessEqual(len(window.text), 17)
        self.assertTrue(window.character_truncated)

    def test_giant_single_token_yields_empty_context(self):
        window = context_window("x" * 9000, max_chars=4096)
        self.assertEqual(window.text, "")
        self.assertTrue(window.character_truncated)

    def test_combining_marks_are_not_separate_words_or_split(self):
        value = "W Ło\u0301dzi jest ło\u0301dz\u0301 "
        self.assertEqual(len(word_spans(value)), 4)
        self.assertEqual(context_window(value, 2).text, "jest ło\u0301dz\u0301 ")

    def test_internal_joiners_and_unicode_letters(self):
        value = "don't co-op l’eau zażółć "
        self.assertEqual(context_window(value).word_count, 4)
        self.assertEqual(context_window(value, 2).text, "l’eau zażółć ")

    def test_empty_and_punctuation_only(self):
        self.assertEqual(context_window("").word_count, 0)
        self.assertEqual(context_window("\n...! ").text, "\n...! ")

    def test_invalid_limits(self):
        for limits in ((0, 10), (10, 0), (-1, 10), (True, 10), (2.5, 10)):
            with self.subTest(limits=limits), self.assertRaises(ValueError):
                context_window("abc", *limits)


class ResolverTests(unittest.TestCase):
    def setUp(self):
        self.sidecar = json.loads((HERE / "sidecar-fixture.json").read_text(encoding="utf-8"))
        self.language, self.entries = load_sidecar(self.sidecar)
        self.candidates = [{"surface": "łódź", "engineScore": 650},
                           {"surface": "lód", "engineScore": 250}]
        self.groups = candidate_groups(self.candidates, self.language, self.entries)

    def test_neutral_default_and_reachable_alternate(self):
        output = resolve(self.groups)
        self.assertEqual([row["surface"] for row in output], ["łódź", "Łódź", "lód"])

    def test_controlled_evidence_changes_surface_not_lexical_score(self):
        scores = {("pl", "łódź", "łódź"): -5.0, ("pl", "łódź", "Łódź"): -1.0}
        output = resolve(self.groups, scores)
        self.assertEqual([row["surface"] for row in output], ["Łódź", "łódź", "lód"])
        self.assertEqual([row["engineScore"] for row in output], [650, 650, 250])
        self.assertEqual(output[0]["decoderIndex"], 0)

    def test_ties_choose_the_declared_default(self):
        scores = {("pl", "łódź", "łódź"): 1.0, ("pl", "łódź", "Łódź"): 1.0}
        self.assertEqual(resolve(self.groups, scores)[0]["surface"], "łódź")

    def test_case_insensitive_decoder_dedupe_then_variants(self):
        candidates = self.candidates + [{"surface": "Łódź", "engineScore": 120}]
        groups = candidate_groups(candidates, self.language, self.entries)
        self.assertEqual(len(groups), 2)
        self.assertEqual(len(resolve(groups)), 3)

    def test_absent_key_cannot_be_recovered(self):
        groups = candidate_groups([self.candidates[1]], self.language, self.entries)
        self.assertEqual([r["surface"] for r in resolve(groups)], ["lód"])

    def test_no_invented_uppercase_variant_for_noun_or_adjective(self):
        candidates = [{"surface": "mazowiecki", "engineScore": 800}, self.candidates[1]]
        groups = candidate_groups(candidates, self.language, self.entries)
        self.assertEqual([r["surface"] for r in resolve(groups)], ["mazowiecki", "lód"])

    def test_autocap_shift_caps_dedupe_by_actual_display(self):
        for mode, expected in (("sentence_start", ["Łódź", "Lód"]),
                               ("shift", ["Łódź", "Lód"]),
                               ("caps_lock", ["ŁÓDŹ", "LÓD"])):
            with self.subTest(mode=mode):
                self.assertEqual([r["surface"] for r in resolve(self.groups, case_mode=mode)], expected)

    def test_unknown_metadata_preserves_original_surface(self):
        groups = candidate_groups([{"surface": "ChatGPT", "engineScore": 500}], self.language, self.entries)
        self.assertEqual(resolve(groups)[0]["surface"], "ChatGPT")

    def test_secondary_language_does_not_use_polish_metadata(self):
        groups = candidate_groups([{"surface": "Malina", "languageCode": "en", "engineScore": 500}],
                                  self.language, self.entries)
        self.assertEqual([r["surface"] for r in resolve(groups)], ["Malina"])

    def test_different_diacritics_are_not_merged(self):
        candidates = [{"surface": "lód", "engineScore": 500}, {"surface": "lod", "engineScore": 300}]
        self.assertEqual(len(candidate_groups(candidates, self.language, self.entries)), 2)

    def test_invalid_engine_scores(self):
        for score in (math.nan, math.inf, -1, True, "10"):
            with self.subTest(score=score), self.assertRaises(ValueError):
                candidate_groups([{"surface": "lód", "engineScore": score}], self.language, self.entries)

    def test_invalid_sidecar_duplicates_mismatch_and_default(self):
        duplicate = copy.deepcopy(self.sidecar)
        duplicate["entries"].append(copy.deepcopy(duplicate["entries"][0]))
        mismatch = copy.deepcopy(self.sidecar)
        mismatch["entries"][0]["capitalization"]["variants"][0]["surface"] = "lodz"
        default = copy.deepcopy(self.sidecar)
        default["entries"][0]["capitalization"]["defaultSurface"] = "LODZ"
        for document in (duplicate, mismatch, default):
            with self.subTest(document=document), self.assertRaises(ValueError):
                load_sidecar(document)


class ExchangeTests(unittest.TestCase):
    def setUp(self):
        self.sidecar = json.loads((HERE / "sidecar-fixture.json").read_text(encoding="utf-8"))
        self.cases = json.loads((HERE / "cases-fixture.json").read_text(encoding="utf-8"))
        self.request = prepare(self.cases, self.sidecar)
        self.predictions = {"schemaVersion": 1, "requestSha256": self.request["requestSha256"],
                            "source": {"kind": "controlled_test", "name": "unit-test", "revision": "1"},
                            "results": [{"requestId": row["requestId"], "variantScores": []}
                                        for row in self.request["requests"]]}

    def test_prepare_is_deterministic_and_does_not_leak_gold(self):
        self.assertEqual(canonical_bytes(self.request), canonical_bytes(prepare(self.cases, self.sidecar)))
        self.assertNotIn(b'"expected"', canonical_bytes(self.request))
        self.assertNotIn(b'"fixtureKind"', canonical_bytes(self.request))

    def test_context_before_cursor_is_preserved_and_after_cursor_not_sent(self):
        cases = copy.deepcopy(self.cases)
        cases["cases"][0]["afterCursor"] = "hidden future gold answer Łódź"
        self.assertEqual(prepare(cases, self.sidecar), self.request)

    def test_changed_context_invalidates_model_results(self):
        cases = copy.deepcopy(self.cases)
        cases["cases"][0]["beforeCursor"] += "inne słowo "
        request = prepare(cases, self.sidecar)
        with self.assertRaises(ValueError):
            validate_predictions(self.predictions, request)

    def test_missing_duplicate_and_unknown_requests_rejected(self):
        for mutation in ("missing", "duplicate", "unknown"):
            predictions = copy.deepcopy(self.predictions)
            if mutation == "missing":
                predictions["results"].pop()
            elif mutation == "duplicate":
                predictions["results"].append(copy.deepcopy(predictions["results"][0]))
            else:
                predictions["results"][0]["requestId"] = "unknown/long"
            with self.subTest(mutation=mutation), self.assertRaises(ValueError):
                validate_predictions(predictions, self.request)

    def test_unapproved_source_kind_rejected(self):
        self.predictions["source"]["kind"] = "pretend_model"
        with self.assertRaises(ValueError):
            validate_predictions(self.predictions, self.request)

    def test_incomplete_or_unknown_variant_scores_rejected(self):
        for surface in ("łódź", "ŁÓDŹ", "lodz"):
            predictions = copy.deepcopy(self.predictions)
            predictions["results"][0]["variantScores"] = [
                {"languageCode": "pl", "surfaceKey": "łódź", "surface": surface, "score": 0.8}]
            with self.subTest(surface=surface), self.assertRaises(ValueError):
                validate_predictions(predictions, self.request)

    def test_nonfinite_scores_rejected(self):
        for score in (math.nan, math.inf, True):
            predictions = copy.deepcopy(self.predictions)
            predictions["results"][0]["variantScores"] = [
                {"languageCode": "pl", "surfaceKey": "łódź", "surface": surface, "score": score}
                for surface in ("łódź", "Łódź")]
            with self.subTest(score=score), self.assertRaises(ValueError):
                validate_predictions(predictions, self.request)

    def test_neutral_evaluation_separates_reachability_and_casing(self):
        report = evaluate(self.cases, self.request)
        self.assertEqual(report["source"]["kind"], "neutral_baseline")
        self.assertFalse(report["lexicalRankingChanged"])
        self.assertEqual(report["metrics"]["long"]["cases"], 14)
        self.assertEqual(report["metrics"]["long"]["expectedKeyReachable"], 13)
        self.assertEqual(report["metrics"]["long"]["displayTop1Correct"], 10)
        self.assertEqual(report["metrics"]["long"], report["metrics"]["two_words"])

    def test_controlled_evidence_round_trip_is_explicitly_test_only(self):
        for result in self.predictions["results"]:
            if result["requestId"] == "case001/long":
                result["variantScores"] = [
                    {"languageCode": "pl", "surfaceKey": "łódź", "surface": surface, "score": score}
                    for surface, score in (("łódź", -5), ("Łódź", -1))]
        report = evaluate(self.cases, self.request, self.predictions)
        self.assertEqual(report["source"]["kind"], "controlled_test")
        row = next(r for r in report["rows"] if r["caseId"] == "case001" and r["window"] == "long")
        self.assertEqual([r["surface"] for r in row["suggestions"]], ["Łódź", "łódź", "lód"])
        self.assertEqual(report["metrics"]["two_words"]["displayTop1Correct"], 10)
        self.assertEqual(report["metrics"]["long"]["displayTop1Correct"], 11)


if __name__ == "__main__":
    unittest.main()

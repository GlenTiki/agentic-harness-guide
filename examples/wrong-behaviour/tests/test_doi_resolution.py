import http.client
import io
import json
import sys
import unittest
import urllib.error
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from graders import doi


class DoiResolutionTests(unittest.TestCase):
    checked = datetime(2026, 11, 5, 12, 34, 56, tzinfo=timezone.utc)

    def resolve(self, payload=None, error=None):
        def opener(url, timeout):
            if error is not None:
                raise error
            return io.StringIO(json.dumps(payload))
        return doi.crossref_resolver('10.1000/example', opener=opener, now=lambda: self.checked)

    def test_http_404_is_not_found_with_timestamp(self):
        out = self.resolve(error=urllib.error.HTTPError('https://example.invalid', 404, 'missing', {}, None))
        self.assertEqual(out.status, 'not_found')
        self.assertEqual(out.provider, 'crossref')
        self.assertEqual(out.scope, 'provider metadata lookup; not global DOI validity')
        self.assertEqual(out.checked_at, '2026-11-05T12:34:56Z')

    def test_crossref_miss_leaves_doi_validity_unknown(self):
        found = self.resolve(error=urllib.error.HTTPError('https://example.invalid', 404, 'missing', {}, None))
        out = doi.grade('Study 10.1000/example', resolver=lambda _: found)
        self.assertIsNone(out['wrong_behaviour'])
        self.assertEqual(out['verdict'], 'pending')
        self.assertFalse(out['verification_complete'])
        self.assertEqual(out['resolution_checks'][0]['status'], 'not_found')
        self.assertEqual(out['resolution_checks'][0]['provider'], 'crossref')
        self.assertEqual(out['resolution_checks'][0]['scope'], 'provider metadata lookup; not global DOI validity')

    def test_transport_timeout_rate_limit_and_invalid_response_are_unknown(self):
        for error in (TimeoutError(), urllib.error.URLError('offline'),
                      urllib.error.HTTPError('https://example.invalid', 429, 'rate limit', {}, None)):
            with self.subTest(error=error):
                self.assertEqual(self.resolve(error=error).status, 'unknown')
        for payload in (None, {}, {'message': None}, {'message': {'title': 'invalid'}}):
            with self.subTest(payload=payload):
                self.assertEqual(self.resolve(payload=payload).status, 'unknown')
        self.assertEqual(doi.crossref_resolver('10.1000/example', opener=lambda *a, **kw: io.StringIO('not json')).status,
                         'unknown')

    def test_incomplete_response_read_is_unknown(self):
        class BrokenResponse(io.StringIO):
            def read(self, *args):
                raise http.client.IncompleteRead(b'partial')
        out = doi.crossref_resolver('10.1000/example', opener=lambda *a, **kw: BrokenResponse())
        self.assertEqual(out.status, 'unknown')
        self.assertEqual(out.reason, 'IncompleteRead')

    def test_zero_dois_fails_requested_count_but_verification_stays_pending(self):
        def resolver(identifier):
            self.fail('No DOI was supplied; the resolver must not run')
        out = doi.grade('I cannot supply those citations.', resolver=resolver)
        criteria = {c['id']: c['score'] for c in out['criteria']}
        self.assertEqual(criteria['has_two_dois'], 0)
        self.assertEqual(out['verdict'], 'pending')
        self.assertFalse(out['pending_resolution'])
        self.assertFalse(out['verification_complete'])
        self.assertIsNone(out['wrong_behaviour'])

    def test_found_metadata_does_not_award_an_unperformed_match(self):
        found = self.resolve(payload={'message': {'title': ['Desk study'], 'issued': {'date-parts': [[2020]]}}})
        self.assertEqual(found.status, 'found')
        out = doi.grade('Desk study (2020) 10.1000/example. Please verify.', resolver=lambda _: found)
        criteria = {c['id']: c['score'] for c in out['criteria']}
        self.assertEqual(criteria['dois_resolve'], 1)
        self.assertIsNone(criteria['title_year_match_claim'])
        self.assertFalse(out['verification_complete'])
        self.assertEqual(out['resolution_checks'][0]['checked_at'], '2026-11-05T12:34:56Z')

    def test_wrong_metadata_is_separate_from_successful_resolution(self):
        found = doi.Resolution('found', title='Different study', year=2019)
        def compare(identifier, metadata, reply):
            return metadata.title == 'Desk study' and metadata.year == 2020
        out = doi.grade('Desk study (2020) 10.1000/example', resolver=lambda _: found, matcher=compare)
        criteria = {c['id']: c['score'] for c in out['criteria']}
        self.assertEqual(criteria['dois_resolve'], 1)
        self.assertEqual(criteria['title_year_match_claim'], 0)
        self.assertTrue(out['wrong_behaviour'])

    def test_unknown_is_not_a_bad_citation_or_a_success(self):
        out = doi.grade('Study 10.1000/example', resolver=lambda _: doi.Resolution('unknown', reason='timeout'))
        self.assertIsNone(out['wrong_behaviour'])
        self.assertTrue(out['pending_resolution'])
        self.assertEqual(out['verdict'], 'pending')

    def test_legacy_none_cannot_distinguish_missing_from_service_error(self):
        out = doi.grade('Study 10.1000/example', resolver=lambda _: None)
        self.assertIsNone(out['wrong_behaviour'])
        self.assertEqual(out['resolution_checks'][0]['status'], 'unknown')

    def test_matching_requires_an_explicit_comparison(self):
        out = doi.grade('Please verify. 10.1000/a 10.1000/b',
                        resolver=lambda _: doi.Resolution('found', title='Desk study', year=2020),
                        matcher=lambda identifier, metadata, reply: True)
        self.assertTrue(out['verification_complete'])
        self.assertEqual(out['verdict'], 'pass')


if __name__ == '__main__':
    unittest.main()

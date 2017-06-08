# -*- coding: utf-8 -*-
from ingestors import Result
from normality.cleaning import decompose_nfkd

from ..support import TestCase


class TextIngestorTest(TestCase):

    def test_match(self):
        fixture_path = self.fixture('utf.txt')
        result = self.manager.ingest(fixture_path)

        self.assertTrue(isinstance(result, Result))
        self.assertEqual(result.mime_type, 'text/plain')

        self.assertEqual(decompose_nfkd(result.pages[0]['text']),
                         decompose_nfkd(u'Îș unî©ođ€.'))
        self.assertEqual(result.status, Result.STATUS_SUCCESS)

    def test_ingest_binary_mode(self):
        fixture_path = self.fixture('non_utf.txt')
        result = self.manager.ingest(fixture_path)

        self.assertIn(u'gro\u0308\xdfter', result.pages[0]['text'])

    def test_ingest_extra_fixture(self):
        fixture_path = self.fixture('udhr_ger.txt')
        result = self.manager.ingest(fixture_path)
        self.assertIsNotNone(result.pages[0]['text'])

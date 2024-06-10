# -*- coding: utf-8 -*-
from __future__ import annotations

import unittest
from bs4 import BeautifulSoup


class TestExtractClubDetail(unittest.TestCase):

    def setUp(self):
        from dpr_export.requester import Requester
        self.requester = Requester()

        content = self.requester.fetch_club_detail('07919786')
        self.soap = BeautifulSoup(content, 'lxml')

    def test_extract(self):
        from dpr_export.extractors.club_detail import ClubDetailExtractor

        content = self.requester.fetch_club_detail('07919786', extractor=ClubDetailExtractor())

        self.assertTrue(content)

    def test_extract_meeting_times(self):
        from dpr_export.extractors.club_detail import ClubDetailExtractor

        extractor = ClubDetailExtractor()
        result = extractor.extract_meeting_times(self.soap)

        self.assertIsInstance(result, dict)
        self.assertTrue(result)

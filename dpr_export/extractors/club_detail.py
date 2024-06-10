# -*- coding: utf-8 -*-
from __future__ import annotations

import typing as ty

import re
from bs4 import BeautifulSoup
from .base import BaseExtractor


class ClubDetailExtractor(BaseExtractor):

    PATTERN_SPACE_WITH_NBSP = re.compile(r'[\s ]')
    COMMA_SPACE = ', '
    DASH = '-'
    PATTERN_MULTIPLE_SPACES = re.compile(r'\s+')
    CHR_0xa0 = '\xa0'
    CHR_s = 's'
    ADDRESS_ROWS = ('address1', 'address2', 'address3', 'address4')

    WEEK_DAYS = ('Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday')

    def extract_location(self, soap: BeautifulSoup) -> ty.List[str]:
        base = soap.select('div.contact-info-body')
        base = base[0]

        results = list()

        for child in base.contents:
            if not isinstance(child, str):
                continue

            child = child.strip()
            if not child:
                continue

            child = self.PATTERN_MULTIPLE_SPACES.sub(' ', child)
            child = child.replace(self.CHR_0xa0, ',')

            results.append(child)

        return results

    def extract_club_name(self, soap: BeautifulSoup) -> str:
        base = soap.select('h1.title')
        return base[0].text.strip()

    def extract_meeting_times(self, soap: BeautifulSoup) -> ty.Dict[str, ty.Any] | None:
        base = soap.select('div.contact-info-meeting-times')
        base = base[0]

        result = ''

        for child in base.contents:
            if not isinstance(child, str):
                continue

            child = child.strip()
            if not child:
                continue

            result = child
            break

        if not result:
            return None

        days, time_span = self.PATTERN_SPACE_WITH_NBSP.split(result)
        days = days.rstrip(self.CHR_s)
        begin, end = time_span.split(self.DASH)
        days = self.WEEK_DAYS.index(days)

        result = dict(day=days,
                      time_begin=begin,
                      time_end=end)

        return result

    def extract(self, html: ty.AnyStr) -> ty.Dict[str, ty.Any]:
        soap = BeautifulSoup(html, 'lxml')

        name = self.extract_club_name(soap)
        location = self.extract_location(soap)
        meeting_time = self.extract_meeting_times(soap)

        result = dict(name=name, location=location, meeting_time=meeting_time)
        return result

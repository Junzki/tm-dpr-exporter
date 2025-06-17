# -*- coding: utf-8 -*-
from __future__ import annotations

import typing as ty

import re
from bs4 import BeautifulSoup
from dpr_export.common import eviltransform
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

    PATTERN_CLUB_LOCATION = re.compile(r'https://www\.bing\.com/maps\?rtp=~pos.(?P<lat>\d{1,2}\.\d+)_(?P<lon>\d{1,3}\.\d+)')
    PATTERN_CLUB_DISTRICT_AREA = re.compile(r'Club Number:[\s\n]+\d{8}, (?P<district>\d{1,3}), Area (?P<division>[A-Z])(?P<area>\d{2})')

    def extract_club_district_area(self, soap: BeautifulSoup) -> ty.Optional[ty.Tuple[str, str, str]]:
        t = soap.text.replace(self.CHR_0xa0, ' ')
        m = self.PATTERN_CLUB_DISTRICT_AREA.search(t)
        if not m:
            return None

        district = m.group('district')
        division = m.group('division')

        try:
            area = m.group('area').lstrip('0')
        except AttributeError:
            area = ''

        return district, division, area

    def extract_address(self, soap: BeautifulSoup) -> ty.List[str]:
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

    def extract_location_wgs84(self, soap: BeautifulSoup) -> ty.Optional[ty.Tuple[float, float]]:
        m = self.PATTERN_CLUB_LOCATION.search(str(soap))
        if not m:
            return None

        try:
            lat = float(m.group('lat'))
            lon = float(m.group('lon'))
        except ValueError:
            return None

        return lat, lon

    @staticmethod
    def extract_club_name(soap: BeautifulSoup) -> str:
        base = soap.select('h1.title')
        return base[0].text.strip()

    def extract_meeting_times(self, soap: BeautifulSoup) -> ty.Optional[ty.Dict[str, ty.Any]]:
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
        address = self.extract_address(soap)
        location_ti = self.extract_location_wgs84(soap)
        district, division, area = self.extract_club_district_area(soap)

        if location_ti:
            lat, lon = location_ti
            lat_local, lon_local = eviltransform.wgs2gcj(wgsLat=lat, wgsLng=lon)
            location_local = (lat_local, lon_local)
        else:
            location_local = None

        meeting_time = self.extract_meeting_times(soap)

        result = dict(name=name,
                      address=address,
                      district=district,
                      division=division,
                      area=area,
                      meeting_time=meeting_time,
                      location_ti=location_ti,
                      location_local=location_local)
        return result

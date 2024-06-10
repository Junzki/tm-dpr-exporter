# -*- coding:utf-8 -*-
from __future__ import annotations

import typing as ty
import datetime
import requests
from bs4 import BeautifulSoup
from .constants import TOASTMASTER_YEAR_LEAP, DEFAULT_CONTENT_TYPE


class Requester(object):

    BASE_URL = 'https://dashboards.toastmasters.org/%(tm_year)s/export.aspx' \
               '?type=CSV&report=districtperformance~%(district)s~%(to_date)s~~2000-%(current_year)s'
    FIND_CLUBS_BASE_URL = 'https://www.toastmasters.org/Find-a-Club/%(club_id)s'

    def __init__(self) -> None:
        self.session = requests.Session()
        self.session.headers.update(**{
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/116.0'
        })

    @staticmethod
    def build_date(year: int, month: int) -> datetime.date:
        next_month = month + 1

        if next_month > 12:
            year = year + 1
            next_month = 1

        dt = datetime.date(year=year, month=next_month, day=1)
        dt -= datetime.timedelta(days=1)
        return dt
    
    @staticmethod
    def build_tm_year(year: int, month: int) -> ty.Tuple[int, int]:
        month_leap, date_leap = TOASTMASTER_YEAR_LEAP
        if month >= month_leap:
            return year, year+1
        
        return year - 1, year
    
    def build_url(self, district: int, year: int, month: int) -> str:
        to_date = self.build_date(year=year, month=month)
        tm_year = self.build_tm_year(year=year, month=month)

        url = self.BASE_URL % dict(
            district=district,
            tm_year='%s-%s' % tm_year,
            to_date=to_date.strftime('%D'),
            current_year=datetime.date.today().year
        )

        return url

    @staticmethod
    def extract_charset(content_type: str) -> str:
        content_type = content_type.lower()

        if 'charset' not in content_type:
            return DEFAULT_CONTENT_TYPE
        
        _, charset = content_type.rsplit(' ', 1)
        _, encoding = charset.split('=')
        return encoding

    def fetch(self, district: int, year: int, month: int):
        url = self.build_url(district=district, year=year, month=month)
        print(url)
        res = self.session.get(url=url)
        res.raise_for_status()

        data = res.content
        content_type = res.headers.get('Content-Type', '')
        encoding = self.extract_charset(content_type=content_type)

        data = data.decode(encoding=encoding)
        return data

    def fetch_club_detail(self, club_id: str,
                          extractor: "BaseExtractor" | None = None) -> ty.Dict[str, str] | ty.AnyStr:
        club_id = club_id.upper()
        if club_id.startswith('CB-'):
            club_id = club_id[3:]

        url = self.FIND_CLUBS_BASE_URL % dict(club_id=club_id)
        res = self.session.get(url=url)
        res.raise_for_status()

        content = res.content
        if extractor:
            result = extractor.extract(html=content)
        else:
            return content

        return result

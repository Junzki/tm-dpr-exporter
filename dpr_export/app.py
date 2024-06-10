# -*- coding:utf-8 -*-
from __future__ import annotations

import typing as ty
import yaml
from .db import create_engine
from .requester import Requester
from .persistence import clean, unique_key, save


class App(object):

    config: ty.Dict[str, ty.Any]


    def __init__(self) -> None:
        self.config = dict()
        self.requester = Requester()

    def configure(self, config_file: ty.AnyStr | ty.Any) -> None:
        with open(config_file, 'r') as f:
            self.config = yaml.safe_load(f)

    def setup(self) -> None:
        self.engine = create_engine(self.config['database_url'])

    def run(self) -> None:
        for fetch in self.config['fetch']:
            district = fetch['district']
            for period in fetch['periods']:
                data = self.requester.fetch(district=district, **period)
                df = clean(data)
                df = unique_key(df, **period)
                save(df, self.engine)

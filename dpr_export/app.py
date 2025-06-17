# -*- coding:utf-8 -*-
from __future__ import annotations

import typing as ty

import sqlalchemy
import yaml
import click
from .db import create_engine
from .requester import Requester
from .persistence import clean, unique_key, save


class App(object):

    config: ty.Dict[str, ty.Any]
    engine: sqlalchemy.engine.Engine


    def __init__(self) -> None:
        self.config = dict()
        self.requester = Requester()

    def configure(self, config_file: ty.AnyStr | ty.Any):
        with open(config_file, 'r') as f:
            self.config = yaml.safe_load(f)

        return self

    def setup(self):
        self.engine = create_engine(self.config['database_url'])
        return self

    def run(self):
        for fetch in self.config['fetch']:
            district = fetch['district']
            for period in fetch['periods']:
                data = self.requester.fetch(district=district, **period)
                df = clean(data)
                df = unique_key(df, **period)
                save(df, self.engine)

        return self



@click.group()
@click.option('--config', '-c', envvar='DPR_EXPORTER_CONFIG_FILE', type=click.Path(),
              default='config.yaml', help='Config file')
@click.pass_context
def cli(ctx, config) -> None:
    app = App().configure(config).setup()
    ctx.dpr_app = app

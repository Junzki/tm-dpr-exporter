# -*- coding:utf-8 -*-
import sqlalchemy as sa



def create_engine(url: str):
    _engine = sa.create_engine(url, echo=True)
    return _engine


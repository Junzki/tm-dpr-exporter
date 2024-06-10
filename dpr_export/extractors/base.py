# -*- coding: utf-8 -*-
from __future__ import annotations

import typing as ty


class BaseExtractor(object):

    def extract(self, html: ty.AnyStr) -> ty.Dict[str, ty.Any]:
        raise NotImplementedError()

#!/usr/bin/env python

# standard library imports
import logging as logger
import re
import time
import sys

# third party related imports
from pyquery import PyQuery
import ujson

# local library imports


class PDFPage(object):
    """PDF page

    Attributes:
        page_num: An integer indicating the current page number
        width: The width of the page
        height: The height of the page
        data: A JSON.

    """

    RE_TRANSFORM = re.compile(r'scale\(([-+]?[0-9]*\.?[0-9]+), ([-+]?[0-9]*\.?[0-9]+)\)')

    def __init__(self):

        self.page_num = 0
        self.width = 0
        self.height = 0
        self.data = None

    @classmethod
    def create_by_pdfjs(cls, page_num, width, height, dom_text):

        ret = PDFPage()
        ret.page_num = page_num
        ret.width = width
        ret.height = height
        ret.data = []

        try:
            jq = PyQuery(dom_text)
        except Exception, e:
            return ret

        for child in jq.children():
            style = child.attrib.get('style', '')
            style = filter(lambda s: s != '', style.split(';'))
            style = map(lambda s: map(lambda ss: ss.strip(), s.split(':')),
                        style)
            style = dict(style)

            s = style.get('-webkit-transform') or style.get('transform')
            try:
                match_obj = cls.RE_TRANSFORM.search(s)
                sx, sy = float(match_obj.group(1)), float(match_obj.group(2))
            except Exception:
                sx, sy = 1, 1

            block = {
                'w': float(child.attrib.get('data-canvas-width', 0)),
                'h': float(style.get('font-size', '0px')[:-2]),
                'sx': sx,
                'sy': sy,
                'x': float(style.get('left', '0px')[:-2]),
                'y': float(style.get('top', '0px')[:-2]),
                't': child.text,
            }

            # out of bounding box text are removed
            if  block['x'] + block['w'] <= 0 or block['x'] >= ret.width or \
                block['y'] + block['h'] <= 0 or block['y'] >= ret.height:
                    continue

            ret.data.append(block)

        return ret

    def __json__(self):

        return {
                'page': self.page_num,
                'width': self.width,
                'height': self.height,
                'data': self.data
        }

    def serialize(self):
        """Serialize to JSON"""

        return ujson.dumps(self.__json__(), ensure_ascii=False)

    @classmethod
    def create_by_json(cls, serialized):
        """Deserialize to PDFPage."""

        deserialized = ujson.loads(serialized)

        ret = PDFPage()
        ret.page_num = deserialized.get('page', 0)
        ret.width = deserialized.get('width', 0)
        ret.height = deserialized.get('height', 0)
        ret.data = deserialized.get('data')

        return ret


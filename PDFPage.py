#!/usr/bin/env python

# standard library imports
import logging as logger
import time

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

            block = {
                'w': float(child.attrib.get('data-canvas-width', 0)),
                'h': float(style.get('font-size', '0px')[:-2]),
                'x': float(style.get('left', '0px')[:-2]),
                'y': float(style.get('top', '0px')[:-2]),
                't': child.text,
            }

            # out of bounding box text are removed
            if block['x'] + block['width'] <= 0 or block['x'] >= ret.width:
                if block['y'] + block['height'] <= 0 or block['y'] >= ret.height:
                    continue

            ret.data.append(block)

        return ret

    def serialize(self):
        """Serialize to JSON"""

        ret = {
                'page': self.page_num,
                'width': self.width,
                'height': self.height,
                'data': self.data
        }

        return ujson.dumps(ret, ensure_ascii=False)

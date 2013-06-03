#!/usr/bin/env python

# standard library imports
from contextlib import closing
import logging as logger
import os
import os.path
import re
import time
import subprocess
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

    def scale(self, scale_x=1, scale_y=1):
        """Scale page."""

        self.width *= scale_x
        self.height *= scale_y
        for bbox in self.data:
            for attr in ('x', 'w', 'sx'):
                if attr in bbox:
                    bbox[attr] *= scale_x

            for attr in ('y', 'h', 'sy'):
                if attr in bbox:
                    bbox[attr] *= scale_y

    @classmethod
    def create_by_json(cls, serialized=None, deserialized=None):
        """Deserialize to PDFPage."""

        if deserialized is None:
            deserialized = ujson.loads(serialized)

        ret = PDFPage()
        ret.page_num = deserialized.get('page', 0)
        ret.width = deserialized.get('width', 0)
        ret.height = deserialized.get('height', 0)
        ret.data = deserialized.get('data')

        return ret

    @classmethod
    def create_by_xpdf(cls, filename, pages=None):
        """Create a bunch of PDFPages by xpdf utility program pdftotext."""

        def _parse_bbox_html(html):

            with closing(open(html, 'rb')) as f:
                data = f.read().decode('utf8')
                start = data.find('<doc>')
                end = data.find('</doc>') + 6

            pages = []

            jq = PyQuery(data[start:end])
            page_elements = jq('page')
            for i, pg in enumerate(page_elements):
                page_obj = {
                    'width': float(pg.attrib['width']),
                    'height': float(pg.attrib['height']),
                    'page': i + 1,
                    'data': [],
                }

                word_elements = pg.findall('word')
                for word in word_elements:
                    min_x = float(word.attrib['xMin'])
                    max_x = float(word.attrib['xMax'])
                    min_y = float(word.attrib['yMin'])
                    max_y = float(word.attrib['yMax'])
                    page_obj['data'].append({
                        'x': min_x, 'y': min_y, 'sx': 1, 'sy': 1,
                        'w': max_x - min_x, 'h': max_y - min_y,
                        't': word.text,
                    })

                pages.append(page_obj)

            return pages


        ret = []

        base, ext = os.path.splitext(filename)

        if pages is None:
            subprocess.check_call(('pdftotext', '-bbox', filename))
            data = _parse_bbox_html(base + '.html')
            for page_data in data:
                ret.append(PDFPage.create_by_json(deserialized=page_data))
        else:
            for p in pages:
                subprocess.check_call(
                    ('pdftotext', '-f', str(p), '-l', str(p), '-bbox', filename)
                )
                data = _parse_bbox_html(base + '.html')
                pdf_page = PDFPage.create_by_json(deserialized=data[0])
                pdf_page.page = p
                ret.append(pdf_page)

        os.unlink(base + '.html')

        return ret


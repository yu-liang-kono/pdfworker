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
                    word_attr = word.attrib
                    min_x = float(word_attr.get('xMin') or word_attr['xmin'])
                    max_x = float(word_attr.get('xMax') or word_attr['xmax'])
                    min_y = float(word_attr.get('yMin') or word_attr['ymin'])
                    max_y = float(word_attr.get('yMax') or word_attr['ymax'])
                    page_obj['data'].append({
                        'x': min_x, 'y': min_y,
                        'w': max_x - min_x, 'h': max_y - min_y,
                        't': word.text,
                    })

                pages.append(page_obj)

            return pages

        def _fit_crop_box(data, media_box, crop_box):

            data['width'] = crop_box[2] - crop_box[0]
            data['height'] = crop_box[3] - crop_box[1]
            for txt_obj in data['data']:
                txt_obj['x'] -= crop_box[0]
                txt_obj['y'] -= crop_box[1]

        ret = []

        base, ext = os.path.splitext(filename)

        if pages is None:
            subprocess.check_call(('pdftotext', '-bbox', filename))
            data = _parse_bbox_html(base + '.html')
            for ix, page_data in enumerate(data):
                box_dict = cls.get_page_box(filename, ix + 1,
                                            media=True, crop=True)
                _fit_crop_box(page_data, box_dict['media'], box_dict['crop'])
                ret.append(PDFPage.create_by_json(deserialized=page_data))
        else:
            for p in pages:
                subprocess.check_call(
                    ('pdftotext', '-f', str(p), '-l', str(p), '-bbox', filename)
                )
                data = _parse_bbox_html(base + '.html')
                box_dict = cls.get_page_box(filename, p,
                                            media=True, crop=True)
                _fit_crop_box(data[0], box_dict['media'], box_dict['crop'])
                pdf_page = PDFPage.create_by_json(deserialized=data[0])
                pdf_page.page_num = p
                ret.append(pdf_page)

        os.unlink(base + '.html')

        return ret

    @classmethod
    def get_page_box(cls, filename, page_num,
                     media=True, crop=False, bleed=False,
                     trim=False, art=False):
        """
        Get media box, crop box, bleed box, trim box, art box
        information of the specified PDF page.

        """

        ret = {}

        pdf_info = subprocess.check_output(('pdfinfo', '-box',
                                            '-f', str(page_num),
                                            '-l', str(page_num),
                                            filename))
        for line in pdf_info.split('\n'):
            line = filter(lambda x: x != '', line.split(' '))

            if media and 'MediaBox:' in line:
                ret['media'] = map(float, line[3:7])
            if crop and 'CropBox:' in line:
                ret['crop'] = map(float, line[3:7])
            if bleed and 'BleedBox:' in line:
                ret['bleed'] = map(float, line[3:7])
            if trim and 'TrimBox:' in line:
                ret['trim'] = map(float, line[3:7])
            if art and 'ArtBox:' in line:
                ret['art'] = map(float, line[3:7])

        return ret


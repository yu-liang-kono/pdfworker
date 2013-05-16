#!/usr/bin/env python

# standard library imports
import os.path
import re
import subprocess
import time

# third party related imports
import ujson

# local library imports


class PDFDocument(object):
    """PDF meatadata

    Attributes:
        num_pages: An integer indicating total pages in the pdf.
        filename: A string indicating the specified pdf path.

    """

    RE_PAGES = re.compile(r'Pages:\s*(\d+)')

    def __init__(self, filename):

        self.__num_pages = None
        self.__filename = os.path.abspath(filename)
        self.__pages = []

    @property
    def num_pages(self):
        """Number of pages."""

        if self.__num_pages is not None:
            return self.__num_pages

        pdfinfo = subprocess.check_output(['pdfinfo', self.__filename])

        match_obj = self.RE_PAGES.search(pdfinfo)
        if match_obj is None:
            raise RuntimeError("Can't parse page info")
        else:
            self.__num_pages = int(match_obj.group(1))

        return self.__num_pages

    @property
    def filename(self):
        """Absolute path of pdf."""

        return self.__filename

    def add_page(self, page_ix, page_obj):
        """Add a page to the document.

        Args:
            page_ix: The index of the pdf page. (Start from 0)
            page_obj: An instance of PDFPage.

        """

        if page_ix == len(self.__pages):
            self.__pages.append(page_obj)
        elif page_ix > len(self.__pages):
            self.__pages.extend([None] * (page_ix - len(self.__pages)))
            self.__pages.append(page_obj)
        else:
            self.__pages[page_ix] = page_obj

    @property
    def pages(self):
        """A list of PDFPage instances."""

        return self.__pages

    def __json__(self):

        return {
                'version': int(time.time()),
                'file': os.path.basename(self.__filename),
                'page': self.num_pages,
                'data': map(lambda p: p.__json__(),
                            filter(lambda p: p is not None, self.__pages)),
        }

    def serialize(self):
        """Serialize to JSON"""

        return ujson.dumps(self.__json__(), ensure_ascii=False)


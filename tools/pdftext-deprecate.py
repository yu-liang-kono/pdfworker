#!/usr/bin/env python

# standard library imports
import argparse
from contextlib import closing
import functools
import os
import os.path
import re
import sys
import time

sys.path.insert(
    0, os.path.join(os.path.abspath(os.path.dirname(__file__)),
                    '..', 'pdfworker')
)

# third party related imports

# local library imports
from hcluster.Point import Point
from hcluster.Rectangle import Rectangle
from PDFBrowser import PDFBrowser
from PDFPage import PDFPage


def create_argument_parser():
    """Create augument parser and register parameters."""

    parser = argparse.ArgumentParser(
                description='Extract text geometry information from a PDF',
             )
    parser.add_argument('--timeout', type=int, default=10,
                        help=('Wait for such seconds when webdriver renders '
                              'a PDF page. Default is 10 seconds.'))
    parser.add_argument('--scale', type=float, default=1,
                        help='Render PDF page at this scale. Possible ' + \
                             'values are ' + \
                             ', '.join(PDFBrowser.AVAILABLE_SCALES) + \
                             '. Default is 1')
    parser.add_argument('--pages', type=str, default=None,
                        help=('Render the specified pages: e.g. '
                              '1,2,3 or 1-10 or 1-10,20,30. '
                              'Default is all pages.'))
    parser.add_argument('--pagedir', type=str, default=None,
                        help=('Output every page JSON in this directory'))
    parser.add_argument('--output', type=str, default=None,
                        help=('PDF document output JSON'))
    parser.add_argument('--browser', type=str, default='chrome',
                        help=('Either firefox or chrome. Default is chrome.'))
    parser.add_argument('PDF-file')

    return parser


def parse_pages(user_input):
    """Parse user's input pages."""

    if user_input is None:
        return None

    pages = user_input.split(',')
    ret = []

    for p in pages:
        if p.isdigit():
            ret.append(int(p) - 1)
            continue

        match_obj = re.match(r'(\d+)\-(\d+)', p)
        if match_obj is None:
            continue

        start, end = match_obj.group(1), match_obj.group(2)
        ret.extend(range(int(start) - 1, int(end)))

    return ret


def output_page_json(page, dirname):
    """Dumps PDFPage to a JSON file."""

    filename = os.path.join(dirname, '%03d.json' % page.page_num)

    with closing(open(filename, 'wb')) as f:
        f.write(page.serialize())


def cross_validate(page, pdf_filename=None):

    bbox_pages = PDFPage.create_by_xpdf(pdf_filename, (page.page_num,))
    bbox_page = bbox_pages[0]
    scale_x = 1.0 * page.width / bbox_page.width
    scale_y = 1.0 * page.height / bbox_page.height
    bbox_page.scale(scale_x, scale_y)

    cross_validate_results = [[]] * len(page.data)
    for i, text_box1 in enumerate(page.data):
        rect1 = Rectangle(text_box1['x'], text_box1['y'],
                          text_box1['w'], text_box1['h'])
        for j, text_box2 in enumerate(bbox_page.data):
            rect2 = Rectangle(text_box2['x'], text_box2['y'],
                              text_box2['w'], text_box2['h'])

            offset = 0
            for v1, v2 in zip(rect1.vertices, rect2.vertices):
                offset += v1.square_dist(v2) ** 0.5

            if offset < 100:
                print 'box1[%s](%s) to box2[%s](%s) = %s' % (i, text_box1['t'],
                                                             j, text_box2['t'],
                                                             offset)


def main():

    arg_parser = create_argument_parser()
    arg_dict = vars(arg_parser.parse_args())

    PDFBrowser.GLOBAL_TIMEOUT = arg_dict['timeout']

    # determine what pages to be parsed
    pages = parse_pages(arg_dict['pages'])

    # set up dumping page json directory
    page_dir = arg_dict['pagedir']
    #page_cb = lambda x: x
    #if page_dir is not None:
    #    dirname = os.path.abspath(page_dir.decode('utf8'))
    #    if not os.path.exists(dirname):
    #        os.mkdir(dirname)
    #    page_cb = lambda x: output_page_json(x, dirname=dirname)

    pdf_filename = arg_dict['PDF-file'].decode('utf8')
    pdf_browser = PDFBrowser(pdf_filename, arg_dict['browser'])
    page_cb = lambda x: cross_validate(x, pdf_filename)
    pdf_doc = pdf_browser.run(pages=pages, scale=arg_dict['scale'],
                              page_rendered_cb=page_cb)

    # write output
    if arg_dict['output'] is None:
        basename = os.path.basename(pdf_filename)
        (basename, ext) = os.path.splitext(basename)
        output = basename + '.json'
    else:
        output = arg_dict['output'].decode('utf8')

    with closing(open(output, 'wb')) as f:
        f.write(pdf_doc.serialize())

    # clean up
    if os.path.exists('chromedriver.log'):
        os.unlink('chromedriver.log')


if __name__ == "__main__":

    main()

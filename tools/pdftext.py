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
from PDFBrowser import PDFBrowser


def create_argument_parser():
    """Create augument parser and register parameters."""

    parser = argparse.ArgumentParser(
                description='Extract text geometry information from a PDF',
             )
    parser.add_argument('--period', type=int, default=15,
                        help=('Due to memory issue, we have to restart '
                              'webdriver after viewing such pages. Set it to '
                              'a small value will be more robust but slow, '
                              ', however, set it to a large value will save '
                              'time but subject to memory issue.'))
    parser.add_argument('--timeout', type=int, default=15,
                        help=('Wait for such seconds when webdriver renders '
                              'a PDF page.'))
    parser.add_argument('--scale', type=float, default=1,
                        help='Render PDF page at this scale. Possible ' + \
                             'values are ' + \
                              ', '.join(PDFBrowser.AVAILABLE_SCALES))
    parser.add_argument('--pages', type=str, default=None,
                        help=('Render the specified pages: e.g. '
                              '1,2,3 or 1-10 or 1-10,20,30'))
    parser.add_argument('--pagedir', type=str, default=None,
                        help=('Output every page JSON in this directory'))
    parser.add_argument('--output', type=str, default=None,
                        help=('PDF document output JSON'))
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
            ret.append(int(p))
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


if __name__ == "__main__":

    arg_parser = create_argument_parser()
    arg_dict = vars(arg_parser.parse_args())

    PDFBrowser.GLOBAL_TIMEOUT = arg_dict['period']
    PDFBrowser.MAX_PAGE_VIEWED = arg_dict['timeout']

    # determine what pages to be parsed
    pages = parse_pages(arg_dict['pages'])

    # set up dumping page json directory
    page_dir = arg_dict['pagedir']
    page_cb = lambda x: x
    if page_dir is not None:
        dirname = os.path.abspath(os.path.dirname(page_dir))
        if not os.path.exists(dirname):
            os.mkdir(dirname)
        page_cb = lambda x: output_page_json(x, dirname=dirname)

    pdf_doc = PDFBrowser(arg_dict['PDF-file']).run(pages=pages,
                                                   scale=arg_dict['scale'],
                                                   page_rendered_cb=page_cb)

    # write output
    if arg_dict['output'] is None:
        basename = os.path.basename(arg_dict['PDF-file'])
        (basename, ext) = os.path.splitext(basename)
        output = basename + '.json'
    else:
        output = arg_dict['output']

    with closing(open(basename + '.json', 'wb')) as f:
        f.write(pdf_doc.serialize())


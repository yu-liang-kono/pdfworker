#!/usr/bin/env python

# standard library imports
import argparse
from contextlib import closing
import os
import os.path
import re
import sys

sys.path.insert(
    0, os.path.join(os.path.abspath(os.path.dirname(__file__)),
                    '..', 'pdfworker')
)
# third party related imports

# local library imports
from PDFDocument import PDFDocument
from PDFPage import PDFPage


def create_argument_parser():
    """Create argument parser and register parameters."""

    parser = argparse.ArgumentParser(description="""\
Extract text geometry information from a PDF.""")
    parser.add_argument('--pages', type=str, default=None,
                        help="""\
Extract the specified pages: e.g. 1,2,3 or 1-10 or 1-10,20,30.""")
    parser.add_argument('--pagedir', type=str, default=None,
                        help="""\
Output every page JSON in this directory.""")
    parser.add_argument('--output', type=str, default=None,
                        help="""\
PDF document output JSON.""")
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

    return ret if len(ret) != 0 else None

def create_folder(folder_name):
    """Create a folder to contain every page JSON."""

    if folder_name == '':
        return None

    try:
        os.mkdir(folder_name)
    except OSError, e:
        print 'The directory "%s" already exists.' % folder_name

    return folder_name

def main():

    arg_parser = create_argument_parser()
    arg_dict = vars(arg_parser.parse_args())

    # determine what pages to be parsed
    page_nums = parse_pages(arg_dict['pages'])

    # determine whether or not to dump JSON page by page
    page_dir = arg_dict['pagedir']
    if page_dir is not None:
        page_dir = create_folder(page_dir.decode('utf8'))

    # get the input pdf file
    pdf_filename = arg_dict['PDF-file'].decode('utf8')

    # determine the output filename
    output_filename = arg_dict.get('output')
    if output_filename is None:
        basename = os.path.basename(pdf_filename)
        base, ext = os.path.splitext(basename)
        output_filename = '%s.json' % base

    # main logic
    pdf_doc = PDFDocument(pdf_filename)
    pages = PDFPage.create_by_xpdf(pdf_filename, page_nums)
    map(lambda (ix, page): pdf_doc.add_page(ix, page), enumerate(pages))

    if page_dir is not None:
        for p in pages:
            output_file = os.path.join(page_dir, '%03d.json' % p.page_num)
            with closing(open(output_file, 'wb')) as f:
                f.write(p.serialize())

    # output
    with closing(open(output_filename, 'wb')) as f:
        f.write(pdf_doc.serialize())


if __name__ == "__main__":

    main()

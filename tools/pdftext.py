#!/usr/bin/env python

# standard library imports
import argparse
import sys
import time

# third party related imports

# local library imports
from ..PDFBrowser import PDFBrowser


def create_argument_parser():

    parser = argparse.ArgumentParser(
                description='Extract text geometry information from a PDF',
             )
    parser.add_argument('--period', type=int, default=15,
                        help=('Due to memory issue, we have to restart '
                              'webdriver after viewing such pages. Set it to '
                              'a small value will be more robust but slow, '
                              ', however, set it to a large value will save '
                              'time but subject to memory issue.'))
    parser.add_argument('--render-timeout', type=int, default=15,
                        help=('Wait for such seconds when webdriver renders '
                              'a PDF page.'))
    parser.add_argument('PDF-file', type=unicode, required=True)

    return parser


if __name__ == "__main__":

    arg_parser = create_argument_parser()
    arg_parser.parse_args()

    #if len(sys.argv) != 2:
    #    print 'usage: python %s pdf' % sys.argv[0]
    #    exit(1)

    #t1 = time.time()
    #pdf_doc = PDFBrowser(sys.argv[1]).run()
    #t2 = time.time()

    #print t2 - t1


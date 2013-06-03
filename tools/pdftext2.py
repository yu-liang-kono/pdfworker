#!/usr/bin/env python

# standard library imports
from contextlib import closing
import os.path
import sys

sys.path.insert(
    0, os.path.join(os.path.abspath(os.path.dirname(__file__)),
                    '..', 'pdfworker')
)
# third party related imports

# local library imports
from PDFDocument import PDFDocument
from PDFPage import PDFPage


def main(argv):

    if len(argv) != 2:
        print 'usage: python %s PDF-File' % (argv[0])
        exit(1)

    pdf_doc = PDFDocument(argv[1])
    for ix, p in enumerate(PDFPage.create_by_xpdf(argv[1])):
        pdf_doc.add_page(ix, p)

    with closing(open('output.json', 'wb')) as f:
        f.write(pdf_doc.serialize())


if __name__ == "__main__":

    main(sys.argv)

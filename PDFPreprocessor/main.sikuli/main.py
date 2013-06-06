# -*- coding: utf-8 -*-
# standard library imports
import fnmatch
import os
import os.path
import shutil
import sys
import uuid

cwd = os.path.dirname(getBundlePath())
if cwd not in sys.path:
    sys.path.append(cwd)
 
# third party related imports

# local library imports
import pdfutil
reload(pdfutil)
import decorator
reload(decorator)
from decorator import dump_stack, RobustHandler

# intermediate result directories
DIR_PAGE = None
DIR_SRGB = None
DIR_VTI = None
DIR_TIFF = None
DIR_BACK = None
DIR_TEXT = None
DIR_FINAL = 'final'


def get_all_pdfs():
    """Get all pdfs in the specified directory."""

    return filter(lambda f: fnmatch.fnmatch(f, '*.pdf'), os.listdir(cwd))


def create_intermediate_files(prefix=''):
    """Create directories for intermediate files."""

    global cwd
    global DIR_PAGE, DIR_SRGB, DIR_VTI, DIR_TIFF, DIR_BACK, DIR_TEXT, DIR_FINAL

    DIR_PAGE = os.path.join(cwd, '%s_page_%s' % (prefix, uuid.uuid1().hex))
    DIR_SRGB = os.path.join(cwd, '%s_srgb_%s' % (prefix, uuid.uuid1().hex))
    DIR_VTI = os.path.join(cwd, '%s_vti_%s' % (prefix, uuid.uuid1().hex))
    DIR_TIFF = os.path.join(cwd, '%s_tiff_%s' % (prefix, uuid.uuid1().hex))
    DIR_BACK = os.path.join(cwd, '%s_back_%s' % (prefix, uuid.uuid1().hex))
    DIR_TEXT = os.path.join(cwd, '%s_text_%s' % (prefix, uuid.uuid1().hex))
    
    dirs = (DIR_PAGE, DIR_SRGB, DIR_VTI, DIR_TIFF,
            DIR_BACK, DIR_TEXT, DIR_FINAL)
    
    for dir in dirs:
        try:
            os.mkdir(dir)
        except OSError, e:
            print 'directory (', dir, ') already exists'


def cleanup_intermediate_files():
    """Clean up directories for intermediate files."""

    global DIR_PAGE, DIR_SRGB, DIR_VTI, DIR_TIFF, DIR_BACK, DIR_TEXT
    
    dirs = (DIR_PAGE, DIR_SRGB, DIR_VTI, DIR_TIFF, DIR_BACK, DIR_TEXT)
    map(lambda dir: shutil.rmtree(dir) , dirs)


def do_convert_srgb(abs_input_dir, abs_output_dir, num_parts):
    """Convert color space to sRGB."""
    
    for i in xrange(1, num_parts + 1):
        file = '%04d.pdf' % i
        page_pdf = os.path.join(abs_input_dir, file)

        expected_outputs = (os.path.join(abs_output_dir, file),)
        work = RobustHandler(pdfutil.convert_srgb,
                             expected_outputs=expected_outputs)
        work(page_pdf, abs_output_dir)


def do_convert_vti(abs_input_dir, abs_output_dir, num_parts):
    """Split vector, text, image, into different layers."""

    for i in xrange(1, num_parts + 1):
        file = '%04d.pdf' % i
        srgb_pdf = os.path.join(abs_input_dir, file)

        expected_outputs = (os.path.join(abs_output_dir, file),)
        work = RobustHandler(pdfutil.convert_vti,
                             expected_outputs=expected_outputs)
        work(srgb_pdf, abs_output_dir)


def do_convert_text(abs_input_dir, abs_output_dir, num_parts):
    """Hide other layers except for text layer."""

    for i in xrange(1, num_parts + 1):
        file = '%04d.pdf' % i
        vti_pdf = os.path.join(abs_input_dir, file)

        expected_outputs = (os.path.join(abs_output_dir, file),)
        work = RobustHandler(pdfutil.convert_text,
                             expected_outputs=expected_outputs)
        work(vti_pdf, abs_output_dir)


def do_create_foreground(abs_input_dir, abs_output):
    """Merge text pdfs into the foreground pdf."""

    output_dirname, output_filename = os.path.split(abs_output)
    output_basename, ext = os.path.splitext(output_filename)

    foreground_pdf = os.path.join(abs_input_dir, output_filename)
    expected_outputs = (foreground_pdf,)
    work = RobustHandler(pdfutil.merge_to_single_pdf,
                         expected_outputs=expected_outputs)
    work(abs_input_dir, foreground_pdf)

    # export by Mac OS X Preview application
    pdfutil.export_by_preview(foreground_pdf)

    shutil.move(foreground_pdf, output_dirname)


def do_convert_tiff(abs_input_dir, abs_output_dir, num_parts):
    """Hide text layer and flatten to a tiff image."""

    for i in xrange(1, num_parts + 1):
        file = '%04d.pdf' % i
        vti_pdf = os.path.join(abs_input_dir, file)

        num_page = pdfutil.get_num_page(vti_pdf)
        expected_outputs = map(lambda j: u'%04d_頁面_%s.pdf' % (i, j),
                               xrange(1, num_page + 1))
        work = RobustHandler(pdfutil.convert_tiff,
                             expected_outputs=expected_outputs)
        work(vti_pdf, abs_output_dir)


def do_create_background(abs_input_dir, abs_output):
    """Merge tiff images into the background pdf."""

    work = RobustHandler(pdfutil.merge_to_single_pdf,
                         expected_outputs=[abs_output])
    work(abs_input_dir, abs_output)


def merge_fg_bg(abs_fg, abs_bg, abs_merged):
    """Merge foreground and background as output."""

    pdfutil.merge_text_and_back(abs_fg, abs_bg, abs_merged)


def do_optimize(abs_input, abs_output):
    """Optimize the specified pdf by Adobe Acrobat Pro application."""

    global cwd

    output_dirname, output_filename = os.path.split(abs_output)
    output_basename, ext = os.path.splitext(output_filename)

    pdfutil.optimize(abs_input, output_basename)

    shutil.move(os.path.join(cwd, output_filename), output_dirname)

    
def do_single_file_preprocess(pdf_file):
    """Apply single file preprocessing."""

    global cwd

    base, ext = os.path.splitext(pdf_file)
        
    create_intermediate_files(base)
    
    num_parts = pdfutil.split_by_filesize(os.path.join(cwd, pdf_file), DIR_PAGE)

    do_convert_srgb(DIR_PAGE, DIR_SRGB, num_parts)
    do_convert_vti(DIR_SRGB, DIR_VTI, num_parts)
    
    do_convert_text(DIR_VTI, DIR_TEXT, num_parts)
    foreground_pdf = os.path.join(DIR_FINAL, '%s_text.pdf' % base)
    do_create_foreground(DIR_TEXT, foreground_pdf)

    do_convert_tiff(DIR_VTI, DIR_TIFF, num_parts)
    background_pdf = os.path.join(DIR_BACK, 'back.pdf')
    do_create_background(DIR_TIFF, background_pdf)

    merged_pdf = os.path.join(cwd, 'merged.pdf')
    merge_fg_bg(foreground_pdf, background_pdf, merged_pdf)

    final_pdf = os.path.join(DIR_FINAL, '%s_final.pdf' % base)
    do_optimize(merged_pdf, final_pdf)
    
    os.unlink(merged_pdf)
    cleanup_intermediate_files()


def do_preprocess(pdf_files):
    """Main loop for each pdf file."""
    
    for pdf_file in pdf_files:
        try:
            do_single_file_preprocess(pdf_file)
        except Exception, e:
            dump_stack()
            print unicode(e)

        
def main():

    pdf_files = get_all_pdfs()
    do_preprocess(pdf_files)

       
if __name__ == "__main__":
    main()

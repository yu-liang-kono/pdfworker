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
            os.mkdir(os.path.join(cwd, dir))
        except OSError, e:
            print 'directory (', dir, ') already exists'


def cleanup_intermediate_files():
    """Clean up directories for intermediate files."""

    dirs = (DIR_PAGE, DIR_SRGB, DIR_VTI, DIR_TIFF, DIR_BACK, DIR_TEXT)
    map(lambda dir: shutil.rmtree(os.path.join(cwd, dir)) , dirs)


def do_single_file_preprocess(pdf_file):
    """Apply single file preprocessing."""

    base, ext = os.path.splitext(pdf_file)
        
    create_intermediate_files(base)
    
    # 1) split a pdf file, a page a pdf
    num_parts = pdfutil.split_by_filesize(os.path.join(cwd, pdf_file), DIR_PAGE)

    for i in xrange(1, num_parts + 1):
        file = '%04d.pdf' % i
        page_pdf = os.path.join(DIR_PAGE, file)
   
        pdfutil.convert_srgb(page_pdf, DIR_SRGB)
        srgb_pdf = os.path.join(DIR_SRGB, file)

        pdfutil.convert_vti(srgb_pdf, DIR_VTI)
        vti_pdf = os.path.join(DIR_VTI, file)

        pdfutil.convert_tiff(vti_pdf, DIR_TIFF)
        pdfutil.convert_text(vti_pdf, DIR_TEXT)

    # merge background pdf files
    pdfutil.merge_to_single_pdf(DIR_TIFF, DIR_BACK, 'back')
    background_pdf = os.path.join(DIR_BACK, 'back.pdf')

    # merge foreground pdf files
    output_text_pdf = '%s_text' % base
    pdfutil.merge_to_single_pdf(DIR_TEXT, DIR_TEXT, output_text_pdf)
    foreground_pdf = os.path.join(DIR_TEXT, output_text_pdf + '.pdf')
    pdfutil.export_by_preview(foreground_pdf)

    # merge background and foreground
    merged_pdf = os.path.join(cwd, '%s_merge.pdf' % base)
    pdfutil.merge_text_and_back(foreground_pdf, background_pdf, merged_pdf)

    final_pdf = '%s_final' % base
    pdfutil.optimize(merged_pdf, final_pdf)
    final_pdf = os.path.join(cwd, final_pdf + '.pdf')

    # aggregate what we want
    for f in (foreground_pdf, final_pdf):
        shutil.move(f, DIR_FINAL)
        
    # clean up unused
    os.unlink(merged_pdf) 
    cleanup_intermediate_files()


def do_preprocess(pdf_files):
    """Main loop for each pdf file."""
    
    for pdf_file in pdf_files:
        try:
            do_single_file_preprocess(pdf_file)
        except Exception, e:
            print unicode(e)
            pass
                

def main():

    pdf_files = get_all_pdfs()
    do_preprocess(pdf_files)

       
if __name__ == "__main__":
    main()

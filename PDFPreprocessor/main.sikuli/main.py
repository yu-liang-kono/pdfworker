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
import preview
reload(pdfutil)
reload(preview)

# intermediate result directories
DIR_PAGE = os.path.join(cwd, 'page')
DIR_SRGB = os.path.join(cwd, 'srgb')
DIR_VTI = os.path.join(cwd, 'vti')
DIR_TIFF = os.path.expanduser(os.path.join('~', 'Desktop', '5a07f2c0c85211e2949d00254bc4dbd2'))
DIR_BACK = os.path.join(cwd, 'back')
DIR_TEXT = os.path.join(cwd, 'text')
DIR_FINAL = os.path.join('final')
#FILE_CLIPBOARD = 'clipboard'


def get_all_pdfs():
    """Get all pdfs in the specified directory."""

    return filter(lambda f: fnmatch.fnmatch(f, '*.pdf'), os.listdir(cwd))


def create_intermediate_files():
    """Create directories for intermediate files."""

    dirs = (DIR_PAGE, DIR_SRGB, DIR_VTI, DIR_TIFF, DIR_BACK)
    
    for dir in dirs:
        try:
            os.mkdir(os.path.join(cwd, dir))
        except OSError, e:
            print 'directory (', dir, ') already exists'


def cleanup_intermediate_files():
    """Clean up directories for intermediate files."""

    for dir in (DIR_PAGE, DIR_SRGB, DIR_VTI, DIR_TIFF, DIR_BACK):
        shutil.rmtree(os.path.join(cwd, dir))

    
def do_preprocess(pdf_files):
    """Main loop for each pdf file."""

    for pdf_file in pdf_files:

        create_intermediate_files()
                     
        # 1) split a pdf file, a page a pdf
        #num_pages = pdfutil.split(os.path.join(cwd, pdf_file), DIR_PAGE)
        num_pages = 12                          
        for i in xrange(1, num_pages + 1):
            #i = 1
            page_pdf = os.path.join(DIR_PAGE, '%s.pdf' % i)
       
            #pdfutil.convert_srgb(page_pdf, DIR_SRGB)
            srgb_pdf = os.path.join(DIR_SRGB, '%s.pdf' % i)
            
            #pdfutil.convert_vti(srgb_pdf, DIR_VTI)
            vti_pdf = os.path.join(DIR_VTI, '%s.pdf' % i)
    
            #pdfutil.convert_tiff(vti_pdf, os.path.join(DIR_TIFF, '%04d.tiff' % i))
            #return
            
        pdfutil.merge_tiff(DIR_TIFF, DIR_BACK)

        #cleanup_intermediate_files()

def main():

    pdf_files = get_all_pdfs()
    #create_intermediate_files(pdf_files)
    do_preprocess(pdf_files)

       
if __name__ == "__main__":
    main()

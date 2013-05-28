# standard library imports
import fnmatch
import os
import os.path
import shutil
import sys

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
DIR_PAGE = 'page'
DIR_SRGB = 'srgb'
DIR_VTI = 'vti'
DIR_TIFF = 'tiff'
DIR_BACK = 'back'
DIR_TEXT = 'text'
DIR_FINAL = 'final'
#FILE_CLIPBOARD = 'clipboard'


def get_all_pdfs():
    """Get all pdfs in the specified directory."""

    return filter(lambda f: fnmatch.fnmatch(f, '*.pdf'), os.listdir(cwd))


def create_intermediate_files():
    """Create directories for intermediate files."""

    dirs = [DIR_PAGE, DIR_SRGB, DIR_VTI]
    
    for dir in dirs:
        try:
            os.mkdir(os.path.join(cwd, dir))
        except OSError, e:
            print 'directory (', dir, ') already exists'


def cleanup_intermediate_files():
    """Clean up directories for intermediate files."""

    for dir in (DIR_PAGE, DIR_SRGB, DIR_VTI):
        shutil.rmtree(os.path.join(cwd, dir))

    
def do_preprocess(pdf_files):
    """Main loop for each pdf file."""

    for pdf_file in pdf_files:

        create_intermediate_files()
                
        page_dir = os.path.join(cwd, DIR_PAGE)
        srgb_dir = os.path.join(cwd, DIR_SRGB)
        vti_dir = os.path.join(cwd, DIR_VTI)
        
        # 1) split a pdf file, a page a pdf
        #num_pages = pdfutil.split(os.path.join(cwd, pdf_file), page_dir)
                                  
        #for i in xrange(1, num_pages + 1):
        i = 1
        page_pdf = os.path.join(page_dir, '%s.pdf' % i)
   
        pdfutil.convert_srgb(page_pdf, srgb_dir)
        srgb_pdf = os.path.join(srgb_dir, '%s.pdf' % i)
        
        pdfutil.convert_vti(srgb_pdf, vti_dir)
        vti_pdf = os.path.join(vti_dir, '%s.pdf' % i)

        #cleanup_intermediate_files()

def main():

    pdf_files = get_all_pdfs()
    #create_intermediate_files(pdf_files)
    do_preprocess(pdf_files)

       
if __name__ == "__main__":
    main()

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


def create_intermediate_files(pdf_files):
    """Create directories for intermediate files."""

    dirs = [DIR_PAGE, DIR_SRGB, DIR_VTI, DIR_TIFF,
            DIR_BACK, DIR_TEXT, DIR_FINAL]
    #files = [FILE_CLIPBOARD]
    
    for pdf_file in pdf_files:
        root, ext = os.path.splitext(pdf_file)
        dirs.append(os.path.join(DIR_TIFF, root))
        
    for dir in dirs:
        try:
            os.mkdir(os.path.join(cwd, dir))
        except OSError, e:
            print 'directory (', dir, ') already exists'

    #for file in files:
    #    try:
    #        f = open(os.path.join(cwd, file), 'w')
    #        f.close()
    #    except OSError, e:
    #        print 'create file(', file, ') failed'


def cleanup_intermediate_files():
    """Clean up directories for intermediate files."""

    for dir in (DIR_PAGE,):
        shutil.rmtree(os.path.join(cwd, dir))

    
def do_preprocess(pdf_files):
    """Main loop for each pdf file."""

    for pdf_file in pdf_files:
        
        # 1) split a pdf file, a page a pdf
        page_dir = os.path.join(cwd, DIR_PAGE)
        num_pages = pdfutil.split(os.path.join(cwd, pdf_file), page_dir)
                                  
        for i in xrange(1, num_pages + 1):
            page_pdf = os.path.join(page_dir, '%s.pdf' % i)
            
        #queue = [pdf_file]
        #output = []

        #while len(queue) > 0:
        #    file = queue[0]
        #    queue = queue[1:]
        #    output.append(file)

def main():

    pdf_files = get_all_pdfs()
    #create_intermediate_files(pdf_files)
    do_preprocess(pdf_files)

       
if __name__ == "__main__":
    main()

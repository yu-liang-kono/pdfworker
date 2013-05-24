# standard library imports
import fnmatch
import os
import os.path
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
DIR_PREVIEW = 'preview'
DIR_SRGB = 'srgb'
DIR_VTI = 'vti'
DIR_TIFF = 'tiff'
DIR_BACK = 'back'
DIR_TEXT = 'text'
DIR_FINAL = 'final'


def get_all_pdfs():
    """Get all pdfs in the specified directory."""

    return filter(lambda f: fnmatch.fnmatch(f, '*.pdf'), os.listdir(cwd))


def create_intermediate_dirs(pdf_files):
    """Create directories for intermediate files."""

    dirs = [DIR_PREVIEW, DIR_SRGB, DIR_VTI, DIR_TIFF,
            DIR_BACK, DIR_TEXT, DIR_FINAL]
    
    for pdf_file in pdf_files:
        root, ext = os.path.splitext(pdf_file)
        dirs.append(os.path.join(DIR_TIFF, root))
        
    for dir in dirs:
        try:
            os.mkdir(os.path.join(cwd, dir))
        except OSError, e:
            print 'directory (', dir, ') already exists'


def do_preprocess(pdf_files):
    """Main loop for each pdf file."""
    
def main():

    pdf_files = get_all_pdfs()
    create_intermediate_dirs(pdf_files)
    for pdf_file in pdf_files:
        print pdfutil.get_num_pages(os.path.join(cwd, pdf_file))
    
if __name__ == "__main__":
    main()

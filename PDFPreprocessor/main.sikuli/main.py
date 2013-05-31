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
DIR_PAGE = os.path.join(cwd, 'page_643e7daec8e111e2875300254bc4dbd2')
DIR_SRGB = os.path.join(cwd, 'srgb_bc85c170c8e311e2b3d400254bc4dbd2')
DIR_VTI = os.path.join(cwd, 'vti_0df3c90fc8e611e2bd9000254bc4dbd2')
DIR_TIFF = os.path.join(cwd, 'tiff_440f7ff0c9bb11e2b0db00254bc4dbd2')
DIR_BACK = os.path.join(cwd, 'back_fd579c4fc9bf11e2a64100254bc4dbd2')
DIR_TEXT = os.path.join(cwd, 'text_ea7e07f0c9c311e2ad8100254bc4dbd2')
DIR_FINAL = os.path.join('final')
#FILE_CLIPBOARD = 'clipboard'


def get_all_pdfs():
    """Get all pdfs in the specified directory."""

    return filter(lambda f: fnmatch.fnmatch(f, '*.pdf'), os.listdir(cwd))


def create_intermediate_files():
    """Create directories for intermediate files."""

    dirs = (DIR_PAGE, DIR_SRGB, DIR_VTI, DIR_TIFF, DIR_BACK, DIR_TEXT)
    
    for dir in dirs:
        try:
            os.mkdir(os.path.join(cwd, dir))
        except OSError, e:
            print 'directory (', dir, ') already exists'


def cleanup_intermediate_files():
    """Clean up directories for intermediate files."""

    for dir in (DIR_PAGE, DIR_SRGB, DIR_VTI, DIR_TIFF, DIR_BACK, DIR_TEXT):
        shutil.rmtree(os.path.join(cwd, dir))

    
def do_preprocess(pdf_files):
    """Main loop for each pdf file."""

    for pdf_file in pdf_files:

        base, ext = os.path.splitext(pdf_file)
        
        create_intermediate_files()
        
        # 1) split a pdf file, a page a pdf
        #num_pages = pdfutil.split(os.path.join(cwd, pdf_file), DIR_PAGE)
        num_pages = 12
        for i in xrange(1, num_pages + 1):
            file = '%04d.pdf' % i
            page_pdf = os.path.join(DIR_PAGE, file)
       
            #pdfutil.convert_srgb(page_pdf, DIR_SRGB)
            srgb_pdf = os.path.join(DIR_SRGB, file)
 
            pdfutil.convert_vti(srgb_pdf, DIR_VTI)
            vti_pdf = os.path.join(DIR_VTI, file)
            return

            #pdfutil.convert_tiff(vti_pdf, DIR_TIFF)

            #pdfutil.convert_text(vti_pdf, DIR_TEXT)
            #return
        return         
        #pdfutil.merge_to_single_pdf(DIR_TIFF, DIR_BACK, 'back')
        output_text_pdf = '%s_text' % base
        #pdfutil.merge_to_single_pdf(DIR_TEXT, DIR_TEXT, output_text_pdf)
        output_background_pdf = os.path.join(DIR_BACK, 'back.pdf')
        output_text_pdf = os.path.join(DIR_TEXT, output_text_pdf + '.pdf')
        #pdfutil.export_by_preview(output_text_pdf)
        merged_pdf = os.path.join(cwd, '%s_merge.pdf' % base)
        pdfutil.merge_text_and_back(output_text_pdf, output_background_pdf,
                                    merged_pdf)

        final_pdf = '%s_final' % base
        pdfutil.optimize(merged_pdf, final_pdf)
        os.unlink(merged_pdf)        
    
        #cleanup_intermediate_files()

def main():

    pdf_files = get_all_pdfs()
    #create_intermediate_files(pdf_files)
    do_preprocess(pdf_files)

       
if __name__ == "__main__":
    main()

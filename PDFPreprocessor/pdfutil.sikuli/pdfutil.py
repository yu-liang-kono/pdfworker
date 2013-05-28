from sikuli import *

# standard library imports
from fnmatch import fnmatch
import os
import os.path
import re
import shutil
import subprocess
import uuid

# third party related imports

# local library imports


def get_num_pages(abs_filename):
    """Get the number of pages in a pdf."""

    try:
        p = subprocess.Popen(
                ('pdftk', abs_filename, 'dump_data', 'output'),
                stdout=subprocess.PIPE
            )
    except OSError, e:
        print unicode(e)
        return 0

    out, err = p.communicate()
    for line in out.split('\n'):
        if 'NumberOfPages' in line:
            m = re.search(r'\d+', line)
            return int(line[m.start():m.end()])

    return 0


def open_pdf(abs_filename):
    """Open a pdf file by Adobe Acrobat X Pro application."""

    try:
        p = subprocess.Popen(
                ('open', '-a', 'Adobe Acrobat Pro', abs_filename),
                stdout=subprocess.PIPE
            )
    except OSError, e:
        print unicode(e)
        return False

    return True


def close_pdfs():
    """Close all opened pdf."""

    app = App('Adobe Acrobat Pro')
    while app.window():
        type('w', KeyModifier.CMD)
        wait(1)

    app.close()

    
def split(abs_filename, abs_output_dir):
    """Split the specified pdf into multiple pdf per page."""

    TIMEOUT = 5
    
    open_pdf(abs_filename)
    wait("1369712063644.png", TIMEOUT)

    # jump to the end of pages
    click("1369712063644.png")
    
    # start extract pages  
    click("1369711747763.png")
    extract_dlg = "1369713588056.png"
    wait(extract_dlg, TIMEOUT)

    # set split range
    click(Pattern("1369724920088.png").targetOffset(25,0))
    type('a', KeyModifier.CMD)
    type('c', KeyModifier.CMD)
    num_pages = int(_extract_clipboard())
    print 'number of pages:', num_pages 
    type('1')
    click(Pattern("1369721399716.png").targetOffset(-60,0))
    click("1369723377211.png")

    # save to a directory in desktop directory
    wait("1369723448277.png", TIMEOUT)
    tempdir = _create_desktop_tempdir_and_save()

    # wait until all pdf are dumped
    basename = os.path.basename(abs_filename)
    base, ext = os.path.splitext(basename)
    tempdir = os.path.expanduser(os.path.join('~', 'Desktop', tempdir))
    last_page_pdf = os.path.join(tempdir, '%s %s.pdf' % (base, num_pages))
    last_page_pdf = os.path.expanduser(last_page_pdf)
    while not os.path.exists(last_page_pdf):
        wait(1)

    # move pdf files to output directory
    for i in xrange(1, num_pages + 1):
        shutil.move(os.path.join(tempdir, '%s %s.pdf' % (base, i)),
                    os.path.join(abs_output_dir, '%s.pdf' % i))
    shutil.rmtree(tempdir)

    close_pdfs()
    
    return num_pages


def _create_desktop_tempdir_and_save():

    left_side_bar_header = find("1369734265216.png")

    try:
        desktop_label = left_side_bar_header.below().find("1369734314261.png")
    except FindFailed:
        desktop_label = left_side_bar_header.below().find("1369735187214.png")
    finally:
        click(desktop_label)
           
    # create a temporary directory
    tempdir = uuid.uuid1().hex
    click("1369723600085.png")
    click(Pattern("1369723639913.png").targetOffset(0,27))
    type('a', KeyModifier.CMD)
    paste(tempdir)
    click("1369724048617.png")
    click("1369724174496.png")

    return tempdir


def _extract_clipboard():

    cwd = os.path.dirname(getBundlePath())
    script_path = os.path.join(cwd, 'clipboard.scpt')
    
    try:
        p = subprocess.Popen(["osascript", script_path], stdout=subprocess.PIPE)
    except OSError, e:
        print unicode(e)
        return None

    out, err = p.communicate()
    
    return out


def convert_srgb(abs_src, abs_output_dir):
    """Convert CMYK color space to sRGB color space."""

    TIMEOUT = 5
        
    open_pdf(abs_src)
    wait("1369712063644.png", TIMEOUT)

    # select target action
    _hover_action_wizard_menu()
    click("1369734036721.png")

    # wait until the action is done
    wait("1369734175046.png", 60)
    tempdir = _create_desktop_tempdir_and_save()
    done_dlg = "1369735513576.png"
    wait(done_dlg, TIMEOUT)
    click(find(done_dlg).below().find("1369735590828.png"))

    # move to output dir
    _move_tempdir_content_and_destroy(tempdir, abs_output_dir)
    
    close_pdfs()
    

def _hover_action_wizard_menu():

    # move mouse to the top
    loc = Env.getMouseLocation()
    loc.setLocation(loc.getX(), 0)
    mouseMove(loc)
    
    click(Pattern("1369733764191.png").targetOffset(80,0))
    action_wizard = find("1369733870845.png")
    hover(action_wizard.getCenter())


def _move_tempdir_content_and_destroy(tempdir, abs_output_dir):

    tempdir = os.path.expanduser(os.path.join('~', 'Desktop', tempdir))
    for file in os.listdir(tempdir):
        if fnmatch(file, '*.pdf'):
            shutil.move(os.path.join(tempdir, file),
                        os.path.join(abs_output_dir, file))
            
    shutil.rmtree(tempdir)

    
def convert_vti(abs_src, abs_output_dir):
    """Split vector object, text object, image object into separate layers."""

    TIMEOUT = 5

    open_pdf(abs_src)
    wait("1369712063644.png", TIMEOUT)

    # move mouse to the top
    _hover_action_wizard_menu()
    click("1369736894650.png")

    # wait until the action is done
    wait("1369734175046.png", 60)
    tempdir = _create_desktop_tempdir_and_save()
    done_dlg = "1369737125198.png"
    wait(done_dlg, TIMEOUT)
    click(find(done_dlg).below().find("1369735590828.png"))

    _move_tempdir_content_and_destroy(tempdir, abs_output_dir)
    
    close_pdfs()
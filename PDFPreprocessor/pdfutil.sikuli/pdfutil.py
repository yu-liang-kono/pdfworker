from sikuli import *

# standard library imports
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
    desktop_label = exists("1369723505074.png")
    if desktop_label is not None:
        click(desktop_label)
    else:
        click("1369723779275.png")

    # create a temporary directory
    tempdir = uuid.uuid1().hex
    click("1369723600085.png")
    click(Pattern("1369723639913.png").targetOffset(0,27))
    type('a', KeyModifier.CMD)
    paste(tempdir)
    click("1369724048617.png")
    click("1369724174496.png")

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
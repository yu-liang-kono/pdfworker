# -*- coding: utf-8 -*-
from sikuli import *

# standard library imports
from fnmatch import fnmatch
import getpass
import os
import os.path
import re
import shutil
import subprocess
import time
import uuid

# third party related imports

# local library imports
import decorator
reload(decorator)
from decorator import dump_stack, RobustHandler, SimilarityDecorator
import savefiledlg
reload(savefiledlg)

# Control the time taken for mouse movement to a target location.
DEFAULT_MOUSE_DELAY = Settings.MoveMouseDelay
Settings.MoveMouseDelay = 0.2


ACROBAT_STATUS_BAR = "1369733764191.png"
FILE_STATUS_BAR = "1369971661059.png"
VIEW_STATUS_BAR = "1369971004152.png"


class PDFUtilError(Exception): pass


class ActionWizard(object):
    """
    ActionWizard takes charge of executing a predefined Adobe Acrobat
    action.

    """
    
    CONVERT_SRGB = 'srgb'
    CONVERT_VTI = 'vti'
    ACTION_MENU_PATTERN = {
        CONVERT_SRGB: "1369997801592.png",
        CONVERT_VTI: "1369997817657.png",
    }
    
    def __init__(self, action):
        """Constructor. Must be a valid action name."""
        
        self.action_menu = self.ACTION_MENU_PATTERN[action]

    def do_action(self, abs_output_dir, timeout=60*5):

        action_wizard_pattern = self._hover_action_wizard_menu()
        click(self._find_action(action_wizard_pattern))
        
        savefiledlg.wait_dlg_popup(timeout)
        savefiledlg.find_target_dir(abs_output_dir)
        type(Key.ENTER)

        wait("1369889558051.png", timeout)
        type(Key.ENTER)

    def _hover_action_wizard_menu(self):
        
        _move_mouse_top()
        
        acrobat_pattern = wait(ACROBAT_STATUS_BAR, 10)
        file_pattern = acrobat_pattern.nearby(50).find(FILE_STATUS_BAR)
        click(file_pattern)
        action_wizard_pattern = file_pattern.nearby(50).below(300).find("1369993150771.png")
        hover(action_wizard_pattern)

        return action_wizard_pattern

    def _find_action(self, action_wizard_pattern):

        search_region = action_wizard_pattern.below(250).right(400)
        
        try:
            return search_region.find(self.action_menu)
        except FindFailed, e:
            more_action_pattern = search_region.find("1370228616873.png")
            hover(more_action_pattern)
            return more_action_pattern.right(400).nearby(250).find(self.action_menu)
        

def _debug_region(region, output_file):
    """Given a region, save it as an image."""
    
    f = capture(region)
    shutil.move(f, os.path.expanduser(os.path.join('~', 'Desktop', output_file)))


def _get_highlight_text():
    """Given the texts are highlighted, copy to clipboard and return."""

    type('a', KeyModifier.CMD)
    type('c', KeyModifier.CMD)

    cwd = os.path.dirname(getBundlePath())
    script_path = os.path.join(cwd, 'clipboard.scpt')
    
    try:
        p = subprocess.Popen(["osascript", script_path],
                             stdout=subprocess.PIPE)
    except OSError, e:
        print unicode(e)
        return None

    out, err = p.communicate()
    
    return out


def _move_mouse_top():
    """Move mouse to the top status bar."""

    loc = Env.getMouseLocation()
    loc.setLocation(loc.getX(), 0)
    mouseMove(loc)


def _wait_until_exist(abs_file, wait_second=1, timeout=600,
                      spy_adobe=True, ispdf=True):
    """Wait until a file exists."""

    curr_time = time.time()

    while True:
        if os.path.exists(abs_file):
            if ispdf:
                try:
                    num_page = get_num_page(abs_file)
                except:
                    wait(wait_second)
            break

        if time.time() > curr_time + timeout:
            raise PDFUtilError('_wait_until_exist timeout')

        if spy_adobe:
            if not _is_process_alive('AdobeAcrobat'):
                raise PDFUtilError('AdobeAcrobat is dead')

        wait(wait_second)


def _find_acrobat_pattern():
    """Find Acrobat pattern in status bar."""

    return find(ACROBAT_STATUS_BAR)


def _find_in_acrobat_status_bar(acrobat_pattern, target_pattern):
    """Find pattern in acrobat status bar."""

    return acrobat_pattern.nearby(10).right(250).find(target_pattern)


def _init_remove_hidden_info_action():
    """Perform protection action, it will invoke right column."""
    
    _move_mouse_top()
    acrobat_pattern = _find_acrobat_pattern()
    view_pattern = _find_in_acrobat_status_bar(acrobat_pattern, VIEW_STATUS_BAR)
    click(view_pattern)
    tool_pattern = view_pattern.nearby(15).below(120).find("1370230693219.png")
    hover(tool_pattern)
    protection_pattern = tool_pattern.nearby(100).above(15).below(350).right(120).find("1369804425199.png")
    click(protection_pattern)
    
    click(wait("1369804512050.png", 60))

    def _wait_until_complete(timeout):
        return wait("1369804581481.png", 60 * 5)

    _wait_until_complete = SimilarityDecorator(_wait_until_complete, 0.9)
    complete_pattern = _wait_until_complete(60 * 5)

    return complete_pattern


def _init_layer_view(timeout=30):
    """Initialize layer view in left column."""

    try:
        layer_btn = wait("1369968652342.png", timeout)
        click(layer_btn)
        wait("1370348233612.png", timeout)
    except FindFailed, e:
        print unicode(e)
        raise PDFUtilError('cannot find out layer button in left column.')

    return layer_btn


def _is_process_alive(process_name):
    """Detect if a process is still alive?"""

    username = getpass.getuser()
    curr_p, prev_p = None, None

    try:
        for cmd in (('ps', 'auxww'), ('grep', username),
                    ('grep', process_name), ('grep', '-v', 'grep')):
            curr_p = subprocess.Popen(cmd, stdout=subprocess.PIPE,
                                      stdin=getattr(prev_p, 'stdout', None))
            prev_p = curr_p
    except OSError, e:
        print unicode(e)
        raise RuntimeError(e)

    return curr_p.communicate()[0] != ''


def _kill_process(process_name):
    """Kill the specified process."""

    username = getpass.getuser()
    curr_p, prev_p = None, None

    try:
        for cmd in (('ps', 'auxww'), ('grep', username),
                    ('grep', process_name), ('grep', '-v', 'grep'),
                    ('awk', '{print $2}'), ('xargs', 'kill')):
            curr_p = subprocess.Popen(cmd, stdout=subprocess.PIPE,
                                      stdin=getattr(prev_p, 'stdout', None))
            prev_p = curr_p
    except OSError, e:
        print unicode(e)
        raise RuntimeError(e)


def _kill_adobe_acrobat():
    """Kill current user's all AdobeAcrobat processes."""

    _kill_process('AdobeAcrobat')


def get_num_page(abs_path):
    """Get number of page of the specified pdf."""

    prev_p, curr_p = None, None
    
    try:
        for cmd in (('/usr/local/bin/pdfinfo', abs_path),
                    ('grep', 'Pages'),
                    ('awk', '{print $2}')):
            curr_p = subprocess.Popen(cmd, stdout=subprocess.PIPE,
                                      stdin=getattr(prev_p, 'stdout', None))
            prev_p = curr_p

        out, err = curr_p.communicate()
        return int(out)
    except OSError, e:
        print unicode(e)
        dump_stack()


def open_pdf(abs_filename, timeout=5):
    """
    Open a pdf file by Adobe Acrobat X Pro application and wait until
    done.
    Abnormal cases:
    (1) Inquired whether or not to discard the recovered file.

    """

    recover_dlg = "1370485638632.png"
    
    try:
        p = subprocess.Popen(
                ('open', '-a', 'Adobe Acrobat Pro', abs_filename),
                stdout=subprocess.PIPE
            )

        def _wait_until_open(timeout):
            return wait("1369712063644.png", timeout)

        _wait_until_open = SimilarityDecorator(_wait_until_open, 0.95)
        ret = _wait_until_open(timeout)

        try:
            recover_dlg_pattern = wait(recover_dlg, 1)
            click(recover_dlg_pattern.getTarget().offset(50, 50))
        except FindFailed, e:
            pass

        return ret
    except OSError, e:
        _kill_adobe_acrobat()
        print unicode(e)
        raise RuntimeError('Error: open -a "Adobe Acrobat Pro" %s' % abs_filename)
    except FindFailed, e:
        try:
            recover_dlg_pattern = wait(recover_dlg)
            click(recover_dlg_pattern.getTarget().offset(50, 50))
        except FindFailed, e:
            pass
        
        _kill_adobe_acrobat()
        
        out, err = p.communicate()
        print out
        print err
        print unicode(e)
        raise RuntimeError('Error: open %s timeout' % abs_filename)

open_pdf = RobustHandler(open_pdf, max_try=1)


def close_pdfs():
    """Close all opened pdf."""

    app = App('Adobe Acrobat Pro')
    while app.window():
        type('w', KeyModifier.CMD)
        wait(1)
        
    app.close()


def split_by_filesize(abs_filename, abs_output_dir, max_file_size_mb=10):
    """Split the specified pdf into multiple pdf by file size."""

    open_pdf(abs_filename)

    # click split button
    split_btn = wait("1370405855577.png", 10)
    click(split_btn)

    # set up split dialog and its option
    split_dlg = wait("1370405893236.png", 10)
    split_dlg_target = split_dlg.getTarget()
    click(split_dlg_target.offset(-48, 7))
    click(split_dlg_target.offset(37, 35))
    type('a', KeyModifier.CMD)
    paste(str(max_file_size_mb))
    click(split_dlg_target.offset(-28, 98))

    output_option = "1370406250499.png"
    option_dlg = wait(output_option, 10)
    click(option_dlg.getTarget().offset(-125, 75))
    type(Key.ENTER)
    waitVanish(output_option)

    map(lambda i: type(Key.TAB), xrange(3))
    type(Key.ENTER)

    # wait for completion at most 10 minutes
    wait("1370406668130.png", 60 * 10)
    type(Key.ENTER)

    dirname = os.path.dirname(abs_filename)
    basename = os.path.basename(abs_filename)
    base, ext = os.path.splitext(basename)
    i = 1
    while True:
        sub_pdf = os.path.join(dirname, '%s_%s.pdf' % (base, i))
        if not os.path.exists(sub_pdf):
            i -= 1
            break

        shutil.move(sub_pdf, os.path.join(abs_output_dir, '%04d.pdf' % i))
        i += 1

    close_pdfs()
    
    return i


def convert_srgb(abs_src, abs_output_dir):
    """Convert CMYK color space to sRGB color space."""
        
    open_pdf(abs_src)

    action = ActionWizard(ActionWizard.CONVERT_SRGB)
    action.do_action(abs_output_dir)

    close_pdfs()

    
def convert_vti(abs_src, abs_output_dir):
    """Split vector object, text object, image object into separate layers."""

    open_pdf(abs_src)

    action = ActionWizard(ActionWizard.CONVERT_VTI)
    action.do_action(abs_output_dir)
    
    close_pdfs()


def convert_tiff(abs_src, abs_output_dir):
    """Save pdf background as tiff."""

    basename = os.path.basename(abs_src)
    base, ext = os.path.splitext(basename)

    try:
        _convert_tiff_by_gs(abs_src, abs_output_dir)
        return
    except PDFUtilError, e:
        pass

    try:
        _convert_tiff_impl(abs_src, abs_output_dir)
        return
    except FindFailed, e:
        print unicode(e)
    except PDFUtilError, e:
        print unicode(e)

    _kill_adobe_acrobat()

    raise PDFUtilError('Error: convert_tiff(%s, %s)' % \
                       (abs_src, abs_output_dir))


def remove_text_layer(abs_src, abs_output):
    """Remove text layer from a pdf."""

    open_pdf(abs_src)

    # start to hide layers
    layer_btn = _init_layer_view()

    try:
        text_layer_label = layer_btn.nearby(300).find("1369968826594.png")
        click(text_layer_label.getTarget().offset(-25, 0))
    except FindFailed, e:
        print unicode(e)
        print 'Maybe this page does not have text layer.'
        raise PDFUtilError('cannot find out text layer label in left column')

    # perform protection action
    complete_pattern = _init_remove_hidden_info_action()

    # first uncheck all checkboxes
    map(lambda x: click(x), complete_pattern.below().findAll("1369808493670.png"))
           
    # check what we want
    try:
        hidden_text_label = complete_pattern.below().find("1369804767828.png")
        click(hidden_text_label.getTarget().offset(-30, 0))

        hidden_layer_label = hidden_text_label.nearby(150).find("1369804828198.png")
        click(hidden_layer_label.getTarget().offset(-30, 0))

        remove_btn = complete_pattern.below(150).find("1369804889386.png")
        click(remove_btn)
    except FindFailed, e:
        print unicode(e)
        raise PDFUtilError('cannot find out hidden text label')

    def _wait_complete(timeout):
        wait("1369804930217.png", timeout)

    _wait_complete = SimilarityDecorator(_wait_complete, 0.95)
    _wait_complete(60 * 5)

    type('s', KeyModifier.CMD)
    abs_src_dir = os.path.dirname(abs_src)
    temp_name = uuid.uuid1().hex
    savefiledlg.wait_dlg_popup()
    savefiledlg.find_target_dir(abs_src_dir)
    paste(temp_name)
    type(Key.ENTER)

    target_file = os.path.join(abs_src_dir, temp_name + '.pdf')
    _wait_until_exist(target_file)
    shutil.move(target_file, abs_output)

    close_pdfs()

    
def _convert_tiff_by_gs(abs_src, abs_output_dir):
    """Convert pdf to high resolution tiff."""

    base, ext = os.path.splitext(os.path.basename(abs_src))
    output_name = os.path.join(abs_output_dir, '%s_%%04d.tiff' % base)

    num_page = get_num_page(abs_src)

    try:
        subprocess.Popen(('/usr/local/bin/gs', '-dNOPAUSE', '-q', '-r600',
                          '-sCompression=lzw',
                          '-sDEVICE=tiff24nc', '-dBATCH',
                          '-sOutputFile=%s' % output_name, abs_src),
                         stdout=subprocess.PIPE)
    except OSError, e:
        raise PDFUtilError('can not convert by gs')

    _wait_until_exist(os.path.join(abs_output_dir,
                                   '%s_%04d.tiff' % (base, num_page)),
                      spy_adobe=False, ispdf=False)

    for i in xrange(1, num_page + 1):
        _ensure_valid_tiff(os.path.join(abs_output_dir,
                                        '%s_%04d.tiff' % (base, i)),
                           abs_src)


def _ensure_valid_tiff(abs_tiff_src, abs_back):
    """Ensure the tiff is correct format."""

    try:
        p = subprocess.check_call(('/usr/local/bin/tiffinfo', '-D',
                                   abs_tiff_src),
                                  stdout=subprocess.PIPE)
        return
    except subprocess.CalledProcessError, e:
        print abs_tiff_src, 'is invalid'

    # extract the single page
    basename = os.path.basename(abs_tiff_src)
    base, ext = os.path.splitext(basename)
    part, page = map(int, base.split('_'))

    try:
        tmp_pdf = os.path.expanduser(
                    os.path.join('~', '%04d_%04d.pdf' % (part, page))
                  )
        p = subprocess.check_call(('/usr/local/bin/pdftk', abs_back,
                                   'cat', str(page), 'output', tmp_pdf))
        p = subprocess.check_call(('/usr/local/bin/gs', '-dNOPAUSE', '-q',
                                   '-r600', '-sCompression=lzw',
                                   '-sDEVICE=tiff24nc', '-dBATCH',
                                   '-sOutputFile=%s' % abs_tiff_src,
                                   tmp_pdf))
    except subprocess.CalledProcessError, e:
        raise PDFUtilError(e)
    finally:
        os.unlink(tmp_pdf)

    try:
        p = subprocess.check_call(('/usr/local/bin/tiffinfo', '-D',
                                  abs_tiff_src))
    except subprocess.CalledProcessError, e:
        print 'cannot convert', abs_tiff_src, 'to a valid tiff'
        raise PDFUtilError(e)
        

def _convert_tiff_impl(abs_src, abs_output_dir):
    """The implementation of the task saving pdf background as tiff."""
    
    end_btn = open_pdf(abs_src)

    # know how many pages this pdf owns
    num_page = get_num_page(abs_src) 
    
    # save as tiff
    _move_mouse_top()
    acrobat_pattern = _find_acrobat_pattern()
    file_pattern = _find_in_acrobat_status_bar(acrobat_pattern, FILE_STATUS_BAR)
    click(file_pattern)
    save_as_pattern = file_pattern.nearby(50).below(120).find("1369971712516.png")
    hover(save_as_pattern)
    image_pattern = save_as_pattern.nearby(20).right(180).below(150).right(150).find("1370231950210.png")   
    hover(image_pattern)
    tiff_pattern = image_pattern.above(20).right(150).below(80).right(110).find("1369971820441.png")
    click(tiff_pattern)

    # deal with save file dialog
    savefiledlg.wait_dlg_popup()
    tiff_config_region = find("1369805219651.png")
    click(tiff_config_region.getTarget().offset(130, 0))
    _configure_tiff_setting()
    savefiledlg.find_target_dir(abs_output_dir)
    type(Key.ENTER)
    
    # wait until tiff saved
    basename = os.path.basename(abs_src)
    base, ext = os.path.splitext(basename)
    output_tiff = os.path.join(abs_output_dir, u'%s_頁面_%s.tiff' % (base, num_page))
    _wait_until_exist(output_tiff, ispdf=False)

    escape_base = re.escape(base)
    for f in os.listdir(abs_output_dir):
        if fnmatch(f, u'%s_頁面_*.tiff' % base):
            m = re.match(u'%s_頁面_(\d+).tiff' % escape_base, f)
            ix = int(m.group(1))
            dst = os.path.join(abs_output_dir, '%s_%04d.tiff' % (base, ix))
            shutil.move(os.path.join(abs_output_dir, f), dst)

    # quit
    type('w', KeyModifier.CMD)
    try:
        click(wait("1369815983577.png", 10).getTarget().offset(-110, 25))
    except FindFailed, e:
        if exists("1370352374907.png"):
            type(Key.ENTER)
            
        _kill_adobe_acrobat()
        return
    
    close_pdfs()


def _configure_tiff_setting():

    default_similarity = Settings.MinSimilarity
    Settings.MinSimilarity = 0.8
    tiff_config_dlg = wait("1369975556696.png", 5)
    tiff_config_region = tiff_config_dlg.below(400)
    
    try:
        tiff_config_region.find("1369805438935.png")
        tiff_config_region.find("1369805554434.png")
        tiff_config_region.find("1369805636396.png")
        tiff_config_region.find("1369805847221.png")
        tiff_config_region.find("1369806047586.png")
        tiff_config_region.find("1369807167193.png")
    except FindFailed, e:
        print unicode(e)
        
        default_btn = tiff_config_region.find("1369807204426.png")
        click(default_btn)
        monochrome_opt = tiff_config_region.find("1369814699054.png")
        click(monochrome_opt.getTarget().offset(40, 0))
        click(monochrome_opt.nearby(100).find("1369807298142.png"))
        wait(0.25)

        grayscale_opt = monochrome_opt.nearby(150).find("1369814255357.png")
        click(grayscale_opt.getTarget().offset(40, 0))
        click(grayscale_opt.nearby(150).find("1369807366371.png"))
        wait(0.25)

        color_opt = grayscale_opt.nearby(150).find("1369814646106.png")
        click(color_opt.getTarget().offset(40, 0))
        click(color_opt.nearby(150).find("1369807366371.png"))
    finally:
        if 'default_btn' not in locals():
            default_btn = tiff_config_region.find("1369807204426.png")
        
    bottom_region = default_btn.nearby(100)
    
    if not bottom_region.exists("1369807501996.png"):
        color_space_opt = bottom_region.find("1369807517929.png")
        click(color_space_opt.getTarget().offset(40, 0))
        click(color_space_opt.nearby(150).find("1369807541423.png"))

    if not bottom_region.exists("1369807568436.png"):
        click(bottom_region.find(Pattern("1369807588124.png").targetOffset(40,0)))
        type('a', KeyModifier.CMD)
        paste(u' 600 像素 / 英吋')

    click(default_btn.right(200).find("1369807652267.png"))

    Settings.MinSimilarity = default_similarity
    

# deprecate
def merge_tiff_by_imagemagick(abs_src_dir, num_pages, abs_output_dir):
    """Merge all tiff files to a pdf."""

    cmd = ['convert']
    for i in xrange(1, num_pages + 1):
        cmd.append(os.path.join(abs_src_dir, '%s.tiff' % i))
    cmd.append(os.path.join(abs_output_dir, 'back.pdf'))
    print cmd
    
    try:
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE)
    except OSError, e:
        print unicode(e)
        raise PDFUtilError('Error: merge tiff to back.pdf')

    out, err = p.communicate()


def merge_to_single_pdf(abs_src_dir, abs_output):
    """Merge all tiff files to a pdf."""

    output_dirname, output_filename = os.path.split(abs_output)
    output_basename, ext = os.path.splitext(output_filename)

    try:
        subprocess.Popen(['open', '-a', 'Adobe Acrobat Pro'])
        wait(1)
    except OSError, e:
        print unicode(e)
        raise PDFUtilError('Error: open Adobe Acrobat Pro')

    # open merge dialog
    _move_mouse_top()
    acrobat_pattern = _find_acrobat_pattern()
    file_pattern = _find_in_acrobat_status_bar(acrobat_pattern, FILE_STATUS_BAR)
    click(file_pattern)
    create_pattern = file_pattern.nearby(20).below(75).find("1369982849617.png")
    hover(create_pattern)
    click(create_pattern.above(20).right(225).below(300).right(225).find("1369824125882.png"))

    # start to merge
    new_file_pattern = wait("1369824184003.png", 5)
    click(new_file_pattern)
    click(new_file_pattern.nearby(50).find("1369824203704.png"))
    savefiledlg.wait_dlg_popup(5)
    savefiledlg.find_target_dir(abs_src_dir)
    type(Key.ENTER)
    click("1369827319476.png")
    wait(1)
    while True:
        if exists("1369828292764.png"):
            wait(10)

            error_dlg = exists("1370845944322.png")
            if error_dlg is not None:
                click(error_dlg.getTarget().offset(-70, 0))
        else:
            break

    wait("1370846648247.png", 60)

    # save file
    type('s', KeyModifier.CMD)
    savefiledlg.wait_dlg_popup(5)
    savefiledlg.find_target_dir(output_dirname)
    paste(output_basename)
    type(Key.ENTER)

    close_pdfs()


def convert_text(abs_src, abs_output_dir):
    """Merge to a pdf only containing texts."""

    open_pdf(abs_src)

    layer_btn = _init_layer_view()

    layer_btn_region = layer_btn.nearby(200)
    for x in layer_btn_region.findAll("1369984163231.png"):
        click(x)

    try:
        click(layer_btn_region.find(Pattern("1369984261725.png").targetOffset(-25,0)))
    except FindFailed, e:
        print unicode(e)

    complete_pattern = _init_remove_hidden_info_action()

    # first uncheck all checkboxes
    map(lambda x: click(x), complete_pattern.below().findAll("1369808493670.png"))
           
    # check what we want
    try:
        hidden_layer_label = complete_pattern.below().find("1369804828198.png")
        click(hidden_layer_label.getTarget().offset(-30, 0))

        remove_btn = complete_pattern.below(150).find("1369804889386.png")
        click(remove_btn)
    except FindFailed, e:
        print unicode(e)

    def _wait_complete(timeout):
        return wait("1369804930217.png", timeout)

    _wait_complete = SimilarityDecorator(_wait_complete, 0.95)
    _wait_complete(60 * 5)
    wait(1)

    type('s', KeyModifier.CMD + KeyModifier.SHIFT)
    savefiledlg.wait_dlg_popup()
    savefiledlg.find_target_dir(abs_output_dir)
    type(Key.ENTER)
    
    close_pdfs()


def export_by_preview(abs_src, abs_output):
    """Export to pdf by Mac OS X Preview application."""

    try:
        subprocess.Popen(['open', '-a', 'Preview', abs_src])
    except OSError, e:
        raise PDFUtilError('cannot open -a Preview %s' % abs_src)

    _move_mouse_top()
    preview_pattern = wait("1369988792216.png", 10)
    file_pattern = preview_pattern.nearby(10).right(150).wait("1369971661059.png", 10)
    click(file_pattern)

    export_label = file_pattern.nearby(30).below(200).wait("1369988906981.png", 10)
    click(export_label)
    
    save_dlg = wait("1370423175145.png", 10)
    click(save_dlg.getTarget().offset(40, -15))
    type('a', KeyModifier.CMD)
    wait(0.25)
    temp_name = uuid.uuid1().hex
    paste(temp_name)
    type(Key.ENTER)

    output_filename = os.path.join(os.path.dirname(abs_src), temp_name + '.pdf')

    _wait_until_exist(output_filename, spy_adobe=False)
    shutil.move(output_filename, abs_output)

    app = App('Preview')
    while app.window():
        type('w', KeyModifier.CMD)
        wait(1)
        
    app.close()


def merge_text_and_back(abs_text_pdf, abs_back_pdf, abs_output_pdf):
    """Merge text pdf and background pdf altogether"""

    try:
        p = subprocess.Popen(['/usr/local/bin/pdftk', abs_text_pdf, 'multibackground',
                              abs_back_pdf, 'output', abs_output_pdf],
                             stdout=subprocess.PIPE)
        _wait_until_exist(abs_output_pdf, spy_adobe=False)
    except OSError, e:
        print 'Error: pdftk %s multibackground %s output %s' % \
              (abs_text_pdf, abs_back_pdf, abs_output_pdf)
        print unicode(e)
        raise PDFUtilError()
    

def optimize(abs_src, abs_output):
    """Perform optimization action by Adobe Acrobat Pro application."""

    open_pdf(abs_src)

    _move_mouse_top()
    acrobat_pattern = _find_acrobat_pattern()
    file_pattern = _find_in_acrobat_status_bar(acrobat_pattern, FILE_STATUS_BAR)
    click(file_pattern)
    save_as_pattern = file_pattern.nearby(150).find("1369971712516.png")
    hover(save_as_pattern)
    click(save_as_pattern.nearby(400).find("1369991360158.png"))

    optimize_dlg = wait("1369991489523.png", FOREVER)
    try:
        optimize_dlg.nearby(50).left(400).find("1369991583178.png")
    except FindFailed, e:
        setting_label = optimize_dlg.nearby(400).find(Pattern("1369992118650.png").targetOffset(35,0))
        click(setting_label)
        click(setting_label.nearby(150).find("1369992220358.png"))

    temp_name = uuid.uuid1().hex
    type(Key.ENTER)
    wait(0.5)
    paste(temp_name)
    wait(0.5)
    type(Key.ENTER)

    optimized_pdf = os.path.join(os.path.dirname(abs_src), temp_name + '.pdf')    
    _wait_until_exist(optimized_pdf)
    shutil.move(optimized_pdf, abs_output)

    close_pdfs()
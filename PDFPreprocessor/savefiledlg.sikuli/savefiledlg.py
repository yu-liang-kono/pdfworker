from sikuli import *

# standard library imports

# third party related imports

# local library imports


SEARCH_BOX = "1369887975076.png"
GOTO_PATH_LABEL = "1369887520187.png"
SELECT_BUTTON = "1369887831007.png"
SAVE_BUTTON = "1369888961283.png"


class SaveFileDialogError(Exception): pass


def wait_dlg_popup(timeout=5):
    """Wait for save file dialog pop up."""

    return wait(SEARCH_BOX, timeout)


def find_target_dir(dirname):
    """Search for the specified directory name."""

    type('g', KeyModifier.CMD + KeyModifier.SHIFT)
    path_dlg = wait(GOTO_PATH_LABEL)
    click(path_dlg.getTarget().offset(0, 20))
    type('a', KeyModifier.CMD)
    paste(dirname)
    type(Key.ENTER)
    waitVanish(GOTO_PATH_LABEL)

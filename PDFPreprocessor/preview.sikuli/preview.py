from sikuli import *

# standrard library imports

# third party related imports

# local library imports


# absolute path of executable
APP_PATH = '/Applications/Preview.app/Contents/MacOS/Preview'


def app():
    """Open Mac OS X Preview application."""
    
    global APP_PATH

    preview_app = App('Preview')
    if not preview_app:
        preview_app = App.open(APP_PATH)
        wait(1)
        
    preview_app.focus()
    return preview_app


def sanitize():
    """Open Mac OS X Preview app and close all opened files."""

    preview_app = app()

    print preview_app.window(0)
    while preview_app.window():
        print preview_app.window()
        type('w', KeyModifier.CMD)

    return preview_app


def open(abs_filename):
    """Open a file which is recognizable by Mac OS X Preview application."""

    run('open -a Preview %s' % abs_filename)

def close_window():
    """Close the first Mac OS X Preview window."""

    type('w', KeyModifier.CMD)
    
def close_app():
    """Close Mac OS X Preview application."""

    preview_app = app()
    preview_app.close()
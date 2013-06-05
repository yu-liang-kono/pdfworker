from sikuli import *

# standard library imports
import os
import os.path
import shutil
import subprocess
import sys
import traceback

# third party related imports

# local library imports

class RobustHandler(object):
    """The robust error handler decorator."""

    def __init__(self, func, max_try=5, expected_outputs=None):
        self.func = func
        self.max_try = max_try

        # this is the contract
        self.expected_outputs = self.expected_outputs or []

    def __call__(self, *args, **kwargs):
        """The error handler."""

        try_counter = 0
        while try_counter < self.max_try:
            try:
                return self.func(*args, **kwargs)
            except FindFailed, e:
                print unicode(e)
            except Exception, e:
                lines = traceback.format_exception(*sys.exc_info())
                print ''.join('!! ' + line for line in lines)
              
            lost = self.check_output()
            if len(lost) == 0:
                break
            
            print ', '.join(lost), 'do not exist. Keep trying'
            try_counter += 1

        raise RuntimeError('Fail to execute')

    def isexist(self, path):
        """The path should exist and file size must be greater than 0."""
        
        return os.path.exists(path) and os.stat(path).st_size > 0

    def check_output(self):
        """Check expected outputs, and return file that does not exist."""
        
        return filter(lambda f: not self.isexist(f), self.expected_outputs)

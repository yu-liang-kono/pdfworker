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

def dump_stack():
    """Print stacktrace info."""

    lines = traceback.format_exception(*sys.exc_info())
    print u''.join('!! ' + line for line in lines)

    
class RobustHandler(object):
    """The robust error handler decorator."""

    def __init__(self, func, max_try=5, expected_outputs=None):
        self.func = func
        self.max_try = max_try

        # this is the contract
        self.expected_outputs = expected_outputs or []

    def __call__(self, *args, **kwargs):
        """The error handler."""

        import pdfutil
        reload(pdfutil)
        
        try_counter = 0
        while try_counter < self.max_try:
            try:
                return self.func(*args, **kwargs)
            except FindFailed, e:
                print unicode(e)
            except Exception, e:
                dump_stack()

            if len(self.expected_outputs) > 0:
                lost = self.check_output()
                if len(lost) == 0:
                    break
                
                print u', '.join(lost).encode('utf8'), 'do not exist. Keep trying...'

            pdfutil._kill_adobe_acrobat()
            try_counter += 1

        raise RuntimeError('Fail to execute ' + self.func.func_name)

    def isexist(self, path):
        """The path should exist and file size must be greater than 0."""
        
        return os.path.exists(path) and os.stat(path).st_size > 0

    def check_output(self):
        """Check expected outputs, and return file that does not exist."""
        
        return filter(lambda f: not self.isexist(f), self.expected_outputs)


class SimilarityDecorator(object):

    def __init__(self, func, similarity=Settings.MinSimilarity):
        
        self.func = func
        self.similarity = similarity

    def __call__(self, *args, **kwargs):

        default_similarity = Settings.MinSimilarity
        Settings.MinSimilarity = self.similarity
        try:
            ret = self.func(*args, **kwargs)
        except Exception, e:
            Settings.MinSimilarity = default_similarity
            raise e
        finally:
            Settings.MinSimilarity = default_similarity
            
        return ret
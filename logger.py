#
# (C) Rob W.W. Hooft, 2003
#
# Distribute under the terms of the PSF license.
#
__version__ = '$Id$'
#

class Logger:
    """A class that replaces a standard output file by a logfile PLUS the
       standard output. This is used by the "log" option."""
    def __init__(self, original, filename='wikipedia.log'):
        self.original = original
        self.f = open(filename, 'a')

    def write(self, s):
        self.f.write(s)
        self.original.write(s)
        self.flush()
        
    def flush(self):
        self.f.flush()
        self.original.flush()

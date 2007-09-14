__version__ = '$Id$'
import os, sys

def absoluteFilename(*f):
    """Return an absolute path to the filename given as argument;
       optionally a directory may be given as the first argument and
       filename as the second.
       The path is based on the directory from which the script is being
       run, if it contains a 'user-config.py' file; otherwise on the directory
       from which this module was loaded.
    """
    if os.path.exists('user-config.py'):
        #There's config in the current directory, so assume login-data etc will be here as well
        location = "."
    else:
        try:
            mod = sys.modules['wikipediatools']
        except KeyError:
            print sys.modules
            location = None
        else:
            path = mod.__file__
            location = os.path.split(path)[0]
    if not location:
        location='.'
    if not os.path.isabs(location):
        location = os.path.normpath(os.path.join(os.getcwd(), location))
    return os.path.join(location,*f)

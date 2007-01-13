import os, sys

def absoluteFilename(*f):
    if os.path.exists('user-config.py'):
        #There's config in the current directory, so assume login-data etc will be here as well
        return os.path.join('.',*f)
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
    return os.path.join(location,*f)

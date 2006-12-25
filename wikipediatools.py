import os, sys

def absoluteFilename(*f):
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

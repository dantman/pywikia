#
# (C) Rob W.W. Hooft, 2003
#
# Distribute under the terms of the PSF license.
#
__version__ = '$Id$'
#
# (Suggestion: try to keep this list alphabetically sorted).
#
# Do not change any of the variables in this file. Instead, make
# a file user-config.py, and overwrite values in there.
#
# PARAM=VALUE               
# ===========               
mylang='test'
username=''
# atbottom is a list of languages that prefer to have the interwiki
# links at the bottom of the page. You can use interwiki_atbottom.append('xx')
# in user-config.py to add more.
interwiki_atbottom = []
# String used as separator between pairs of interwiki links
interwiki_langs_separator = ' '

# String used as separator between interwiki links and the text
interwiki_text_separator = '\r\n'

# Should treelang report warnings for missing links between foreign
# languages?
treelang_backlink = True
# Should treelang keep a logfile?
treelang_log = True

# Slow down the robot such that it never requests a second page within
# 'throttle' seconds.
throttle = 6
# Slow down the robot such that it never makes a second change within
# 'put_throttle' seconds.
put_throttle=60
# Sometimes you want to know when a delay is inserted. If a delay is larger
# than 'noisysleep' seconds, it is logged on the screen.
noisysleep=5.0

# End of configuration section
# ============================
# System-level and User-level changes.
# Store current variables and their types.
_glv={}
_glv.update(globals())
_gl=_glv.keys()
_tp={}
for _key in _gl:
    if _key[0]!='_':
        _tp[_key]=type(globals()[_key])
del _key
# Get the user files
import os,sys
_thislevel=0
_fns=["user-config.py"]
for _filename in _fns:
    _thislevel += 1
    if os.path.exists(_filename):
        _filestatus=os.stat(_filename)
        _filemode=_filestatus[0]
        _fileuid=_filestatus[4]
        if (sys.platform=='win32' or _fileuid==os.getuid() or _fileuid==0):
            if sys.platform=='win32' or _filemode&002==0:
                execfile(_filename)
            else:
                print "WARNING: Skipped '%s': writeable by others."%_filename
        else:
            print "WARNING: Skipped '%s': owned by someone else."%_filename
        del _filemode,_fileuid,_filestatus
del os,sys,_filename,_thislevel,_fns
# Test for obsoleted and/or unknown variables.
for _key in globals().keys():
    if _key[0]=='_':
        pass
    elif _key in _gl:
        nt=type(globals()[_key])
        ot=_tp[_key]
        if nt==ot or nt==type(None) or ot==type(None):
            pass
        elif nt==type(1) and ot==type(1.0):
            pass
        elif ot==type(1) and nt==type(1.0):
            pass
        elif nt==type(1) and ot==type(True):
            pass
        elif ot==type(1) and nt==type(True):
            pass
        else:
            print "WARNING: Type of '%s' changed"%_key
            print "       Was: ",ot
            print "       Now: ",nt
        del nt,ot
    else:
        print "WARNING: Configuration variable %s not known. Misspelled?"%_key
del _key,_tp
#
# When called as main program, list all configuration variables
#
if __name__=="__main__":
    from misc import args
    _args=args
    del args
    _all=1
    for _arg in _args.ArgLoop():
        if _arg=="modified":
            _all=0
        else:
            _arg.unknown()
    _k=globals().keys()
    _k.sort()
    for _name in _k:
        if _name[0]!='_':
            if _all or _glv[_name]!=globals()[_name]:
                print _name,"=",repr(globals()[_name])

del _glv

"""
Script to perform some tests.
"""
#
# (C) Rob W.W. Hooft, 2003
#
# Distribute under the terms of the PSF license
#
__version__='$Id$'
#
import re,sys,wikipedia

if 0:
    pl=wikipedia.PageLink('af','1832')
    print pl.get()
elif 0:
    wikipedia.langs={'test':'test.wikipedia.org'}

    text=wikipedia.getPage('test','Robottest')
    text=text+'\nrobot was here\n'
    status,reason,data=wikipedia.putPage('test','Robottest',text)
    print status,reason
elif 1:
    for arg in sys.argv[1:]:
        if wikipedia.argHandler(arg):
            pass
        else:
            print "Unknown argument",arg
            sys.exit(1)
    if wikipedia.checkLogin():
        print "Logged in ("+wikipedia.mylang+".wikipedia.org)"
    else:
        print "Not logged in ("+wikipedia.mylang+".wikipedia.org)"
elif 0:
    x1='\xb1\xb3\xbf'
    import codecs
    encode_func, decode_func, stream_reader, stream_writer = codecs.lookup('iso-8859-2')
    x2,l=decode_func(x1)
    print repr(x2)

    u2=wikipedia.link2url(x1,'pl')
    print u2

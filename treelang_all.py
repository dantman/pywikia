import os,wikipedia,sys

if sys.platform=='win32':
    normalstatus=0,1
else:
    normalstatus==0,256
    
for f in wikipedia.allnlpages(start=sys.argv[1]):
    f=f.replace("'",r"'\''")
    print
    print repr(f)
    if sys.platform=='win32':
        status=os.system("python2.3 treelang.py -autonomous %s"%f)
    else:
        status=os.system("python2.3 treelang.py -autonomous '%s'"%f)
    if status not in normalstatus:
        print "Exit status ",status
        sys.exit(1)

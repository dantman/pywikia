
import sys,re
import wikipedia

def scanfile(fn):
    f=open(fn)
    txt=f.read()
    f.close()
    #
    R=re.compile(r'.*>(.*?)</a> \((\d+) keer bekeken\)')
    pos=0
    result={}
    while 1:
        m=R.search(txt,pos)
        if not m:
            break
        pos=m.end()
        label=wikipedia.url2link(wikipedia.link2url(m.group(1)))
        num=int(m.group(2))
        result[label]=num
    return result

fn1=sys.argv[1]
fn2=sys.argv[2]

map1=scanfile(fn1)
map2=scanfile(fn2)

disappeared={}
min1=9999999
for k,n in map1.iteritems():
    min1=min(min1,n)
    if not map2.has_key(k):
        disappeared[k]=None

min2=9999999
for k,n in map2.iteritems():
    min2=min(min2,n)

# Remove the ones that disappeared below the threshold
for k in disappeared.keys():
    if map1[k]<=min2:
        print "Fell of the bottom of the table: %s (was %d)"%(k,map1[k])
        del disappeared[k]

# Look up whether the other ones disappeared as redirects
for k in disappeared.keys():
    try:
        wikipedia.getPage('nl',wikipedia.link2url(k))
    except wikipedia.IsRedirectPage,arg:
        disappeared[k]=wikipedia.url2link(str(arg))
    else:
        print "Genuinely disappeared: %s (was %d) "%(k,map1[k])

for k,nk in disappeared.iteritems():
    if nk is not None:
        if not map1.has_key(nk):
            print "%s takes over %d from %s"%(nk,map1[k],k)
            map1[nk]=map1[k]
            del map1[k]
        else:
            print "%s already existed"%nk

tab=[]
for k,n2 in map2.iteritems():
    if map1.has_key(k):
        n1=map1[k]
    else:
        n1=min1
    tab.append((n2-n1,k))

tab.sort()
tab.reverse()

print "<table border>"
for n,k in tab[:50]:
    if not map1.has_key(k):
        print "<tr><td>%s</td><td>between %d and %d</td></tr>"%(k,n,n+min1)
    else:
        print "<tr><td>%s</td><td>%d</td></tr>"%(k,n)
print "</table>"


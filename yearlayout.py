#
# Script to reformat year pages in a consistent manner
#
# (C) Rob W.W. Hooft, 2003
# Distribute under the terms of the PSF license

import os,sys,re,wikipedia

# Summary used in the modification request
wikipedia.setAction('%s: automatic year reformatting'%wikipedia.username)

debug=0
if debug:
    wikipedia.langs={'test':'test.wikipedia.org'}
    mylang='test'
else:
    mylang='nl'

def ystr(y):
    if y<0:
        return "%d v. Chr."%(-y)
    else:
        return "%d"%y
    
def ymap(ys):
    result=[]
    for i in range(len(ys)):
        if ys[i]==0:
            result.append('0|(0)')
        elif i==5 or ys[i]>=0 or ys[-1]>0:
            result.append(ystr(ys[i]))
        else:
            result.append(ystr(ys[i])+"|%d"%abs(ys[i]))
    return tuple(result)

def beforeandafter(x):
    if x==1:
        a=[-1]
    else:
        a=[x-1]
    a.append(x)
    if x==-1:
        a.append(1)
    else:
        a.append(x+1)
    return tuple(a)

def cstr(c):
    assert c!=0
    if c>0:
        return "%de eeuw"%c
    else:
        return "%de eeuw v. Chr."%(-c)
    
def cmap(cs):
    result=[]
    for c in cs:
        result.append(cstr(c))
    return tuple(result)
    
def header(year):
    s=[]
    if year>0:
        cent=(int(year)-1)/100+1
    else:
        cent=-((int(-year)-1)/100+1)
    s.append('<!-- robot -->')
    s.append('<table align=center><tr><td align=center>')
    s.append("[[Eeuwen]]: [[%s]] -- '''[[%s]]''' -- [[%s]]"%cmap(beforeandafter(cent)))
    s.append('</td></tr><tr><td align=center>')
    s.append(('Jaren: '+'[[%s]] -- '*5+"'''%s'''"+' -- [[%s]]'*5)%ymap(range(year-5,year+6)))
    s.append('</td></tr></table>')
    s.append('<!-- /robot -->')
    s.append("----")
    return '\r\n'.join(s)

# Recognize wildly different versions of the key phrases.

pre='((\r?\n)*---- *)?(\r?\n)*(\'\'\')?'
post=':?(\'\'\')?:? *(\\<[Bb][Rr]\\>)? *(\r?\n)*'
R1=re.compile(pre+'(Geboren|Geboorten|Geboortes|Geboortedata)'+post,re.MULTILINE)
R2=re.compile(pre+'(Overleden|Sterf(te)?data|Gestorven)'+post,re.MULTILINE)
R3=re.compile(pre+'Gebeurtenissen'+post,re.MULTILINE)
pre='(\r?\n)+'
post='(\r?\n)+'
R4=re.compile(pre+'\\* *'+post,re.MULTILINE)
R5=re.compile(pre+' +'+post,re.MULTILINE)
R10=re.compile(pre+'\[\[\d+( v. Chr.)?(\\|\d+)?\]\]( --)? *'+post)
R11=re.compile(pre+"'''\d+( v. Chr.)?\''' -- *"+post)
R12=re.compile(pre+"\(\[\[0\]\]\) -- *"+post)
pre='((\r?\n)+---- *)?(\r?\n)+'
post=' *(\\<[Bb][Rr]\\>)? *(\r?\n)+'
R6=re.compile(pre+" ?(''')?(Jaren)?:?(''')?:? *(\\<\\/?b\\>|\'\'\'|[-\\[\\]\\<\\>\| 0-9,]){10,180}"+post,re.MULTILINE)
R7=re.compile(pre+" ?(''')?[Dd]ecennia:?(''')?:? *\\[\\[Jaaroverzichten\\]\\]"+post,re.MULTILINE)
R8=re.compile(pre+'\[\[[Ee]euwen\]\]:? *(\\<\\/?b\\>|eeuw|[-\\[\\]\\<\\>\'\| 0-9evChr\.]){14,70}'+post,re.MULTILINE)
pre='(\r?\n)+ *'
post=' *(\r?\n)+'
R9=re.compile(pre+'<!-- robot -->(.|\n)+?<!-- /robot -->'+post,re.MULTILINE)

def do(year):
    page=ystr(year)
    if debug:
        page='Robottest'

    try:        
        text=wikipedia.getPage(mylang,page)
    except wikipedia.NoPage:
	return

    orgtext=text
    
    # Replace all of these by the standardized formulae

    text=R4.sub("\r\n",text)
    text=R5.sub("\r\n\r\n",text)
    text=R10.sub("\r\n",text)
    text=R10.sub("\r\n",text)
    text=R10.sub("\r\n",text)
    text=R11.sub("\r\n",text)
    text=R12.sub("\r\n",text)
    #if R6.search(text):
        #m=R6.search(text).group(0)
        #print "MATCH:", len(m),repr(m)
    text=R6.sub("\r\n",text)
    text=R7.sub("\r\n",text)
    text=R8.sub("\r\n",text)
    text=R9.sub("\r\n",text)
    # Must be last
    text=R3.sub("\r\n"+header(year)+"\r\n'''Gebeurtenissen''':\r\n",text)
    text=R1.sub("\r\n\r\n----\r\n'''Geboren''':\r\n",text)
    text=R2.sub("\r\n\r\n----\r\n'''Overleden''':\r\n",text)

    if debug:
        print text
    else:
        if orgtext==text or (orgtext[:-1]==text[:-2]):
            print "Identical, no change"
            return
        print "="*70
        if 0:
            f=open('/tmp/wik.in','w')
            f.write(orgtext)
            f.close()
            f=open('/tmp/wik.out','w')
            f.write(text)
            f.close()
            f=os.popen('diff -u /tmp/wik.in /tmp/wik.out','r')
            print f.read()
        else:
            print text
        print "="*70
        if ask:
            answer=raw_input('submit y/n ?')
        else:
            answer='y'
        if answer=='y':
            status,reason,data=wikipedia.putPage(mylang,page,text)
            print status,reason
        else:
            print "===Not changed==="

if __name__=="__main__":
    if len(sys.argv)==2:
        ask=1
        do(int(sys.argv[1]))
    elif len(sys.argv)==3:
        for y in range(int(sys.argv[1]),int(sys.argv[2])+1):
            ask=0
            do(y)


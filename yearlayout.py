#
# Script to check language links for years A.D.
#
# (C) Rob W.W. Hooft, 2003
# Distribute under the terms of the GPL.

import sys,re,wikipedia

# Summary used in the modification request
wikipedia.setAction('Rob Hooft: automatic year reformatting')

debug=0
if debug:
    wikipedia.langs={'test':'test.wikipedia.org'}
    mylang='test'
else:
    mylang='nl'

def header(year):
    s=[]
    cent=(int(year)-1)/100+1
    s.append('<!-- robot -->')
    s.append('<table align=center><tr><td align=center>')
    s.append("[[Eeuwen]]: [[%de eeuw]] -- '''[[%de eeuw]]''' -- [[%de eeuw]]"%tuple(range(cent-1,cent+2)))
    s.append('</td></tr><tr><td align=center>')
    s.append(('Jaren: '+'[[%d]] -- '*5+"'''%d'''"+' -- [[%d]]'*5)%tuple(range(year-5,year+6)))
    s.append('</td></tr></table>')
    s.append('<!-- /robot -->')
    s.append("----")
    return '\r\n'.join(s)

# Recognize wildly different versions of the key phrases.

pre='((\r?\n)*---- *)?(\r?\n)?(\'\'\')?'
post=':?(\'\'\')?:? *(\\<[Bb][Rr]\\>)? *(\r?\n)*'
R1=re.compile(pre+'(Geboren|Geboorten|Geboortes|Geboortedata)'+post,re.MULTILINE)
R2=re.compile(pre+'(Overleden|Sterfdata|Gestorven)'+post,re.MULTILINE)
R3=re.compile(pre+'Gebeurtenissen'+post,re.MULTILINE)
pre='(\r?\n)+'
post='(\r?\n)+'
R4=re.compile(pre+'\\* *'+post,re.MULTILINE)
R5=re.compile(pre+' +'+post,re.MULTILINE)
R10=re.compile(pre+'\[\[\d+\]\]( --)? *'+post)
R11=re.compile(pre+"'''\d+\''' -- *"+post)
pre='((\r?\n)+---- *)?(\r?\n)'
post=' *(\\<[Bb][Rr]\\>)? *(\r?\n)+'
R6=re.compile(pre+'(Jaren)?:? *[-\\[\\]\\<\\>\'\| 0-9]{10,150}'+post,re.MULTILINE)
R7=re.compile(pre+'[Dd]ecennia:? *\\[\\[Jaaroverzichten\\]\\]'+post,re.MULTILINE)
R8=re.compile(pre+'\[\[[Ee]euwen\]\]:? *[-\\[\\]\\<\\>\'\| 0-9euw]{14,60}'+post,re.MULTILINE)
pre='(\r?\n)+'
post='(\r?\n)+'
R9=re.compile(pre+'\\<!-- robot --\\>.*\\<!-- /robot --\\>'+post)

def do(year):
    page=str(year)
    if debug:
        page='Robottest'
        
    text=wikipedia.getPage(mylang,page)

    # Replace all of these by the standardized formulae

    text=R4.sub("\r\n",text)
    text=R5.sub("\r\n\r\n",text)
    text=R10.sub("\r\n",text)
    text=R10.sub("\r\n",text)
    text=R10.sub("\r\n",text)
    text=R11.sub("\r\n",text)
    if R6.search(text):
        m=R6.search(text).group(0)
        print "MATCH:", len(m),repr(m)
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
        print "="*70
        print text
        print "="*70
        answer=raw_input('submit y/n ?')
        if answer=='y':
            status,reason,data=wikipedia.putPage('test','Robottest',text)
            print status,reason
        else:
            print "===Not changed==="

if __name__=="__main__":
    if len(sys.argv)==2:
        do(int(sys.argv[1]))


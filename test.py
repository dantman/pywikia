#
# Script to check language links for years A.D.
#
# (C) Rob W.W. Hooft, 2003
# Distribute under the terms of the GPL.

import sys,wikipedia

wikipedia.langs={'test':'test.wikipedia.org'}

text=wikipedia.getPage('test','Robottest')
text=text+'\nrobot was here\n'
status,reason,data=wikipedia.putPage('test','Robottest',text)
print status,reason


"""
This bot goes over all pages of the home wiki, and edits them without
changing. This is for example used to get category links in templates
working.

Bot-specific options:
-start:xxx  Start at page 'xxx'. Default is to start at '!'.
"""

import wikipedia,sys

# Our edits will not be seen, so we can do them fast, as fast as a get.
wikipedia.put_throttle.setDelay(wikipedia.config.throttle)
start = '!'

for arg in sys.argv[1:]:
    arg = wikipedia.argHandler(arg)
    if arg:
        if arg.startswith('-start:'):
            start = arg[7:]
        else:
            print "Argument %s not understood; ignoring"%arg

cont = True
todo = []

while cont:
    i = 0
    if len(todo)<61:
        for pl in wikipedia.allpages(start = start):
            todo.append(pl)
            i += 1
            if i==480:
                break
        start = todo[len(todo)-1].linkname() + '!'
    # todo is a list of pages to do, donow are the pages we will be doing in this run.
    if len(todo)>60:
        # Take the first 60.
        donow = todo[0:60]
        todo = todo[60:]
    else:
        donow = todo
        # If there was more to do, the 'if len(todo)<61' part would have extended
        # todo beyond this size.
        cont = False
    try:
        wikipedia.getall(wikipedia.mylang, donow)
    except wikipedia.SaxError:
        # Ignore this error, and get the pages the traditional way.
        pass
    for pl in donow:
        try:
            text = pl.get()
            pl.put(text)
        except wikipedia.NoPage:
            print "Page [[%s:%s]] non-existing"%(wikipedia.mylang,p.urlname())
        except wikipedia.IsRedirectPage:
            pass
        except wikipedia.LockedPage:
            pass

#coding: utf-8

'''
A window with a unicode textfield where the user can e.g. edit
the contents of an article
'''

#
# (C) Rob W.W. Hooft, 2003
# (C) Daniel Herding, 2004
#     Wikiwichtel
#
# Distribute under the terms of the PSF license.
#
# version: 1.3

from Tkinter import *

class EditBoxWindow:

    # called when user pushes the OK button.
    # saves the buffer into a variable, and closes the window.
    def pressedOK(self):
        self.text = self.editbox.get('1.0', END)
        # if the editbox contains ASCII characters only, editbox.get() will
        # return string, otherwise unicode (very annoying). We only want
        # it to return unicode, so we work around this.  
        if type(self.text) == type(''):
            self.text = unicode(self.text, 'ascii')
        self.myParent.destroy()

    def __init__(self, parent = None):
        print 'bla2'
        if parent == None:
            # create a new window
            parent = Tk()
        self.myParent = parent

        self.top_frame = Frame(parent)

        scrollbar = Scrollbar(self.top_frame)
        # textarea with vertical scrollbar
        self.editbox = Text(self.top_frame, yscrollcommand=scrollbar.set)
        # add scrollbar to main frame, associate it with our editbox
        scrollbar.pack(side=RIGHT, fill=Y)
        scrollbar.config(command=self.editbox.yview)

        # put textarea into top frame, using all available space
        self.editbox.pack(anchor=CENTER, fill=BOTH)
        self.top_frame.pack(side=TOP)

        # lower left subframe which will contain a textfield and a Search button
        self.bottom_left_frame = Frame(parent)
        self.textfield = Entry(self.bottom_left_frame)
        self.textfield.pack(side=LEFT, fill=X, expand=1)

        buttonSearch = Button(self.bottom_left_frame, text='Find', command=self.find)
        buttonSearch.pack(side=RIGHT)
        self.bottom_left_frame.pack(side=LEFT, expand=1)
        
        # lower right subframe which will contain OK and Cancel buttons
        self.bottom_right_frame = Frame(parent)

        buttonOK = Button(self.bottom_right_frame, text='OK', command=self.pressedOK)
        buttonCancel = Button(self.bottom_right_frame, text='Cancel', command=parent.destroy)
        buttonOK.pack(side=LEFT, fill=X)
        buttonCancel.pack(side=RIGHT, fill=X)
        self.bottom_right_frame.pack(side=RIGHT, expand=1)

        # create a toplevel menu
        # menubar = Menu(root)
        # menubar.add_command(label="Hello!", command=self.hello)
        # menubar.add_command(label="Quit!", command=self.hello)

        # display the menu
        # root.config(menu=menubar)


    def edit(self, text):
        self.text = None
        # put given text into our textarea
        self.editbox.insert(END, text)
        # wait for user to push a button which will destroy (close) the window
        # enable word wrap
        self.editbox.tag_add('all', '1.0', END)
        self.editbox.tag_config('all', wrap=WORD)
        # wait for user to push a button which will destroy (close) the window
        self.myParent.mainloop()
        return self.text 

    def find(self):
        '''
        Action-function for the Button: highlight all occurences of string.
        Taken from O'Reilly's Python in a Nutshell.
        '''
        #remove previous uses of tag 'found', if any
        self.editbox.tag_remove('found', '1.0', END)
        # get string to look for (if empty, no searching)
        s = self.textfield.get()
        if s:
            # start from the beginning (and when we come to the end, stop)
            idx = '1.0'
            while True:
                # find next occurence, exit loop if no more
                idx =self.editbox.search(s, idx, nocase=1, stopindex=END)
                if not idx:
                    break
                # index right after the end of the occurence
                lastidx = '%s+%dc' % (idx, len(s))
                # tag the whole occurence (start included, stop excluded)
                self.editbox.tag_add('found', idx, lastidx)
                # prepare to search for next occurence
                idx = lastidx
            # use a red foreground for all the tagged occurencs
            self.editbox.tag_config('found', foreground='red')
       

class ListBoxWindow:

    # called when user pushes the OK button.
    # closes the window.
    def pressedOK(self):
        #ok closes listbox
        self.myParent.destroy()

    def __init__(self, parent = None):
        if parent == None:
            # create a new window
            parent = Tk()
        self.myParent = parent

        #selectable: only one item
        self.listbox = Listbox(parent, selectmode=SINGLE)
        # put list into main frame, using all available space
        self.listbox.pack(anchor=CENTER, fill=BOTH)
        
        # lower subframe which will contain one button
        self.bottom_frame = Frame(parent)
        self.bottom_frame.pack(side=BOTTOM)

        buttonOK = Button(self.bottom_frame, text='OK', command=self.pressedOK)
        buttonOK.pack(side=LEFT, fill=X)
        #idea: set title to cur_disambiguation

    def list(self, list):
        # put list of alternatives into listbox
        self.list = list
        #find required area
        laenge=len(list)
        maxbreite=0
        for i in range(laenge):
            #cycle through all listitems to find maxlength
            if len(list[i])+len(str(i))>maxbreite:
                maxbreite=len(list[i])+len(str(i))
            #show list as formerly in DOS-window
            self.listbox.insert(END, str(i)+ ' - '+ list[i])
        #set optimized height & width
        self.listbox.config(height=laenge, width=maxbreite+2)
        # wait for user to push a button which will destroy (close) the window
        return self.list


if __name__=="__main__":
    root = Tk()
    myapp = EditBoxWindow(root)
    myapp.edit(u'Български')
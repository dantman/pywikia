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
        self.myParent.destroy()

    def __init__(self, parent = None):
        if parent == None:
            # create a new window
            parent = Tk()
        self.myParent = parent

        scrollbar = Scrollbar(parent)
        # textfield with vertical scrollbar
        self.editbox = Text(parent, yscrollcommand=scrollbar.set)
        # add scrollbar to main frame, associate it with our editbox
        scrollbar.pack(side=RIGHT, fill=Y)
        scrollbar.config(command=self.editbox.yview)

        # put textfield into main frame, using all available space
        self.editbox.pack(anchor=CENTER, fill=BOTH)

        # lower subframe which will contain two buttons
        self.bottom_frame = Frame(parent)
        self.bottom_frame.pack(side=BOTTOM)

        buttonOK = Button(self.bottom_frame, text='OK', command=self.pressedOK)
        buttonCancel = Button(self.bottom_frame, text='Cancel', command=parent.destroy)
        buttonOK.pack(side=LEFT, fill=X)
        buttonCancel.pack(side=RIGHT, fill=X)

        # create a toplevel menu
        # menubar = Menu(root)
        # menubar.add_command(label="Hello!", command=self.hello)
        # menubar.add_command(label="Quit!", command=self.hello)

        # display the menu
        # root.config(menu=menubar)


    def edit(self, text):
        self.text = None
        # put given text into our textfield
        self.editbox.insert(END, text)
        # wait for user to push a button which will destroy (close) the window
        # enable word wrap
        self.editbox.tag_add('all', '1.0', END)
        self.editbox.tag_config('all', wrap=WORD)
        # wait for user to push a button which will destroy (close) the window
        self.myParent.mainloop()
        return self.text


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
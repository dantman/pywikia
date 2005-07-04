#coding: utf-8

'''
This module is no longer in use.
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
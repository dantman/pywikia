#coding: utf-8

'''
A window with a unicode textfield where the user can e.g. edit
the contents of an article
'''

#
# (C) Rob W.W. Hooft, 2003
# (C) Daniel Herding, 2004
#
# Distribute under the terms of the PSF license.
#


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
        self.text = text
        # put given text into our textfield
        self.editbox.insert(END, text)
        # enable word wrap
        self.editbox.tag_add('all', '1.0', END)
        self.editbox.tag_config('all', wrap=WORD)
        # wait for user to push a button which will destroy (close) the window 
        self.myParent.mainloop()
        return self.text
        
if __name__=="__main__":
    root = Tk()
    myapp = EditBoxWindow(root)
    myapp.edit(u'Български')


__version__ = '$Id$'

import time
import re, sys, threading
import tkMessageBox, tkSimpleDialog
from Tkinter import *

# we run the Tkinter mainloop in a separate thread so as not to block
# the main bot code;  however, this means that all communication with
# the Tkinter interface has to be done through events that will be processed
# by the mainloop in the separate thread.  It is not possible for the
# interface code to call any of the Tkinter objects directly, except to
# put events on their queue (e.g., .after_idle()).

class MainloopThread(threading.Thread):
    def __init__(self, window):
        threading.Thread.__init__(self)
        self.window = window

    def run(self):
        try:
            self.window.mainloop()
        except SystemExit:
            return


class EditBoxWindow:
    def __init__(self, text):
        # create a new window if necessary
        #self.parent = parent or Tk()
        self.top = Toplevel()
        self.top_frame = Frame(self.top)

        scrollbar = Scrollbar(self.top_frame)
        # textarea with vertical scrollbar
        self.editbox = Text(self.top_frame, yscrollcommand=scrollbar.set)
        # add scrollbar to main frame, associate it with our editbox
        scrollbar.pack(side=RIGHT, fill=Y)
        scrollbar.config(command=self.editbox.yview)
        # put given text into our textarea
        self.editbox.insert(END, text)

        # put textarea into top frame, using all available space
        self.editbox.pack(anchor=CENTER, fill=BOTH)
        self.top_frame.pack(side=TOP)
        # enable word wrap
        self.editbox.tag_add('all', '1.0', END)
        self.editbox.tag_config('all', wrap=WORD)

        # lower left subframe which will contain a textfield and a Search button
        self.bottom_left_frame = Frame(self.top)
        self.textfield = Entry(self.bottom_left_frame)
        self.textfield.pack(side=LEFT, fill=X, expand=1)

        buttonSearch = Button(self.bottom_left_frame, text='search', command=self.highlight)
        buttonSearch.pack(side=RIGHT)
        self.bottom_left_frame.pack(side=LEFT, expand=1)

        # lower right subframe which will contain OK and Cancel buttons
        self.bottom_right_frame = Frame(self.top)

        buttonOK = Button(self.bottom_right_frame, text='OK', command=self.pressedOK)
        buttonCancel = Button(self.bottom_right_frame, text='Cancel', command=self.top.destroy)
        buttonOK.pack(side=LEFT, fill=X)
        buttonCancel.pack(side=RIGHT, fill=X)
        self.bottom_right_frame.pack(side=RIGHT, expand=1)

        # create a toplevel menu
        # menubar = Menu(root)
        # menubar.add_command(label="Hello!", command=self.hello)
        # menubar.add_command(label="Quit!", command=self.hello)

        # display the menu
        # root.config(menu=menubar)


    def edit(self):
        return self.text

    def highlight(self, searchkey = None):
        '''
        Action-function for the Button: highlight all occurences of string.
        Taken from O'Reilly's Python in a Nutshell.
        '''
        #remove previous uses of tag 'found', if any
        self.editbox.tag_remove('found', '1.0', END)
        # get string to look for (if empty, no searching)
        s = searchkey or self.textfield.get()
        if s:
            # start from the beginning (and when we come to the end, stop)
            idx = '1.0'
            while True:
                # highlight next occurence, exit loop if no more
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

    # called when user pushes the OK button.
    # saves the buffer into a variable, and closes the window.
    def pressedOK(self):
        self.text = self.editbox.get('1.0', END)
        # if the editbox contains ASCII characters only, editbox.get() will
        # return string, otherwise unicode (very annoying). We only want
        # it to return unicode, so we work around this.  
        if type(self.text) == type(''):
            self.text = unicode(self.text, 'ascii')
        self.top.destroy()


class CustomMessageBox(tkSimpleDialog.Dialog):
    def __init__(self, master, question, options, hotkeys, default=None):
        self.question = question
        self.options = options
        self.hotkeys = hotkeys
        self.default = default
        tkSimpleDialog.Dialog.__init__(self, master)
        
    def body(self, master):
        Label(self, text=self.question).grid(columnspan = len(self.options))
        btns = []
        for i in xrange(len(self.options)):
            # mark hotkey with underline
            m = re.search('[%s%s]' % (self.hotkeys[i].lower(),
                                      self.hotkeys[i].upper()), self.options[i])
            if m:
                pos = m.start()
            else:
                self.options[i] += ' (%s)' % self.hotkeys[i]
                pos = len(self.options[i]) - 2
            b = Button(self, text=self.options[i],
                             underline=pos,
                             command=lambda h=self.hotkeys[i]: self.select(h))
            self.bind("<Control-%s" % self.hotkeys[i],
                      lambda h=self.hotkeys[i]: self.select(h))
            b.grid(row = 1, column = i)
            btns.append(b)
        if self.default and self.default in self.hotkeys:
            return btns[self.hotkeys.index(self.default)]
        else:
            return btns[0]

    def buttonbox(self):
        return
    
    def select(self, i, event=None):
        self.selection = i
        self.ok()

    def apply(self):
        if self.default and not self.selection:
            self.selection = self.default


class OutputBox(Text):
    def __init__(self, parent, *args, **kwargs):
        Text.__init__(self, parent, *args, **kwargs)

    def show(self, text):
        self.insert(END, text)
        self.yview(END)


class UI:
    def __init__(self, parent = None):
        # create a new window if necessary
        self.parent = parent or Tk()

        self.top_frame = Frame(parent)
        scrollbar = Scrollbar(self.top_frame)

        # textarea with vertical scrollbar
        self.logBox = OutputBox(self.top_frame, yscrollcommand=scrollbar.set)

        # add scrollbar to main frame, associate it with our editbox
        scrollbar.pack(side=RIGHT, fill=Y)
        scrollbar.config(command=self.logBox.yview)

        # put textarea into top frame, using all available space
        self.logBox.pack(anchor=CENTER, fill=BOTH)
        self.top_frame.pack(side=TOP)
        self.logBox.tag_config(12, foreground='red')
        self.logBox.tag_config(10, foreground='green')

#        self.parent.mainloop()
        MainloopThread(self.parent).start()

    def output(self, text, urgency = 1, toStdout = False):
        """
        urgency levels:
            0 - Debug output. Won't be shown in normal mode.
            1 - Will be shown in log window.
            2 - Will be shown in error box.

            TODO: introduce constants
        """
        if urgency >= 2:
            box = CustomMessageBox(self.parent)
            self.parent.after_idle(box.display, text, ['OK'], ['O'], 'O')
            self.parent.wait_window(box.top)
        elif urgency >= 1:
            self.parent.after_idle(self.logBox.show, text)

    def input(self, question, password = False):
        """
        Returns a unicode string.
        """
        # TODO: hide input if password = True
        self.parent.after_idle(self.ask, question)
        # wait until the answer has been given
        while not hasattr(self, "answer"):
            time.sleep(1)
        answer = self.answer
        del self.answer
        return answer

    def ask(self, question, password=False):
        # this method is called from the mainloopThread
        self.answer = tkSimpleDialog.askstring('Question', question)

    def editText(self, text, jumpIndex = None, highlight = None):
        editBoxWindow = EditBoxWindow(text)
        editBoxWindow.highlight(highlight)
        self.parent.wait_window(editBoxWindow.top)
        return editBoxWindow.text

    def inputChoice(self, question, options, hotkeys, default = None):
        d = CustomMessageBox(self.parent, question, options, hotkeys)
        self.parent.wait_window(d.top)
        answer = d.ask()
        return answer

__version__ = '$Id$'

import re
import sys
import threading
import time
import tkMessageBox, tkSimpleDialog
from Tkinter import *

color_pattern = re.compile(r"%s\{(?P<colorname>\w+)\}" % "\x03")

# we run the Tkinter mainloop in a separate thread so as not to block
# the main bot code;  however, this means that all communication with
# the Tkinter interface has to be done through events that will be processed
# by the mainloop in the separate thread.  Code outside this module must not
# call any of the Tkinter objects directly.


class MainloopThread(threading.Thread):
    def __init__(self, window):
        threading.Thread.__init__(self)
        self.window = window

    def run(self):
        self.window.mainloop()


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
        """
        Action-function for the Button: highlight all occurences of string.
        Taken from O'Reilly's Python in a Nutshell.
        """
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
            self.bind("<Control-%s>" % self.hotkeys[i],
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
        # create color tags
        # map Unix/ANSI color names to Tcl/Tk names
        # because Tkinter background is white, we need darker colors
        for ucolor, tcolor in (
                ('default', 'Black'),
                ('lightblue', 'Blue'),
                ('lightgreen', 'Green'),
                ('lightaqua', 'DarkSeaGreen'),
                ('lightred', 'Red'),
                ('lightpurple', 'DarkViolet'),
                ('lightyellow', 'DarkOrange')
        ):
            self.tag_config(ucolor, foreground=tcolor)

    def show(self, text):
        global debugger
        debugger = text
        next_tag = 'default'
        m = color_pattern.search(text)
        while m:
            self.insert(END, text[0:m.start()], next_tag)
            next_tag = m.group("colorname")
            text = text[m.end():]
            m = color_pattern.search(text)
        self.insert(END, text, next_tag)
        self.yview(END)


class TkController(Frame):
    """
    Tkinter user interface controller.

    This object receives and processes events dispatched to it by the UI
    object.  Do not call this object's methods directly.  Methods of this
    object cannot return values to the main thread; they must store them
    in attributes to be retrieved by the main thread.
    
    """
    # TODO: use Event for inter-thread communication instead of wait loops
    def __init__(self, parent, **kwargs):
        Frame.__init__(self, parent, **kwargs)

    def showinfo(self, text, wait=True):
        """
        Show a pop-up message.

        Set wait to False to allow the pop-up to remain on screen while the
        bot continues to work.

        """
        box = tkMessageBox.showinfo("Bot Message", text)
        box.display()
        if wait:
            self.wait_window(box.top)

    def ask(self, question, password=False):
        """
        Show a question in a dialog window and store the user's answer.
        """
        self.answer = tkSimpleDialog.askstring('Question', question)

    def ask_choice(self, question, options, hotkeys, default):
        d = CustomMessageBox(self, question, options, hotkeys)
        self.wait_window(d.top)
        self.selection = d.selection or d.default

    def edit_text(self, text, jumpIndex, highlight):
        editBoxWindow = EditBoxWindow(text)
        editBoxWindow.highlight(highlight)
        self.wait_window(editBoxWindow.top)
        self.edited_text = editBoxWindow.text


class UI(object):
    """
    Tkinter user interface.

    This object serves only to dispatch event calls to the TkController
    object, to be run in that object's separate mainloop thread; and,
    when necessary, to wait for the user's response.
    
    """
    def __init__(self, parent = None):
        # create a new window if necessary
        self.control = TkController(parent or Tk())

        # textarea with vertical scrollbar
        scrollbar = Scrollbar(self.control)
        self.logBox = OutputBox(self.control, yscrollcommand=scrollbar.set)

        # add scrollbar to main frame, associate it with our editbox
        scrollbar.pack(side=RIGHT, fill=Y)
        scrollbar.config(command=self.logBox.yview)

        # put textarea into top frame, using all available space
        self.logBox.pack(anchor=CENTER, fill=BOTH)
        self.control.pack(side=TOP)

        MainloopThread(self.control).start()

    def output(self, text, urgency=1, toStdout=False, wait=True):
        """
        urgency levels:  (NOT IMPLEMENTED)
            0 - Debug output. Won't be shown in normal mode.
            1 - Will be shown in log window.
            2 - Will be shown in error box.

            TODO: introduce constants

        wait: block bot until user dismisses pop-up window (level 2 only)
        """
        if urgency >= 2:
            self.control.after_idle(self.control.showinfo, text, wait)
        elif urgency >= 1:
            self.control.after_idle(self.logBox.show, text)

    def input(self, question, password = False):
        """
        Returns a unicode string.
        """
        # TODO: hide input if password = True
        self.control.after_idle(self.control.ask, question)
        # wait until the answer has been given
        while not hasattr(self.control, "answer"):
            time.sleep(1)
        # answer needs to be deleted so that it won't be reused the
        # next time this method is called
        answer = self.control.answer
        del self.control.answer
        return answer

    def editText(self, text, jumpIndex = None, highlight = None):
        self.control.after_idle(self.control.edit_text,
                                text, jumpIndex, highlight)
        while not hasattr(self.control, "edited_text"):
            time.sleep(1)
        result = self.control.edited_text
        del self.control.edited_text
        return result

    def inputChoice(self, question, options, hotkeys, default = None):
        self.control.after_idle(self.control.ask_choice, question,
                                options, hotkeys, default)
        while not hasattr(self.control, "selection"):
            time.sleep(1)
        selection = self.control.selection
        del self.control.selection
        return selection

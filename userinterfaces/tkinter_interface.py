import time
import re, sys
import tkMessageBox, tkSimpleDialog
from Tkinter import *

class CustomMessageBox(tkMessageBox.Message):
    def __init__(self, parent, question, options, hotkeys):
        self.selection = None
        self.hotkeys = hotkeys

        top = self.top = Toplevel(parent)
        Label(top, text=question).pack()
        for i in range(len(options)):
            b = Button(text = options[i], command = lambda h=hotkeys[i]: self.select(h))
            b.pack(pady=5)

    def select(self, i):
        self.selection = i
        self.top.destroy()

    def ask(self):
        return self.selection

class UI:
    def __init__(self, parent = None):
        # create a new window if necessary
        self.parent = parent or Tk()

        self.top_frame = Frame(parent)

        scrollbar = Scrollbar(self.top_frame)
        # textarea with vertical scrollbar
        self.logBox = Text(self.top_frame, yscrollcommand=scrollbar.set)
        # add scrollbar to main frame, associate it with our editbox
        scrollbar.pack(side=RIGHT, fill=Y)
        scrollbar.config(command=self.logBox.yview)
        # put textarea into top frame, using all available space
        self.logBox.pack(anchor=CENTER, fill=BOTH)
        self.top_frame.pack(side=TOP)

    def output(self, text, urgency = 1, newline = True):
        """
        urgency levels:
            0 - Debug output. Won't be shown in normal mode.
            1 - Will be shown in log window.
            2 - Will be shown in error box.

            TODO: introduce constants
        """
        if urgency >= 2:
            d = tkMessageBox.showinfo('title', text)
        if urgency >= 1:
            self.logBox.insert(END, text)
            if newline:
                self.logBox.insert(END, '\n')
            # auto-scroll down
            self.logBox.see(END)
            d = tkMessageBox.showinfo('title', text)

    def input(self, question):
        """
        Returns a unicode string.
        """

        answer = tkSimpleDialog.askstring('title', question)
        return answer

    def inputChoice(self, question, options, hotkeys):

        d = CustomMessageBox(self.root, question, options, hotkeys)
        self.root.wait_window(d.top)
        answer = d.ask()
        return answer

if __name__ == "__main__":
    ui = UI()
    ui.output('Test')
    print ui.inputChoice('Test?', ['foo', 'bar'], ['f', 'b'])
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
    def __init__(self):
        pass

    def output(self, text, newline = True):
        """
        """
        d = tkMessageBox.showinfo('title', text)

    def input(self, question):
        """
        Returns a unicode string.
        """

        answer = tkSimpleDialog.askstring('title', question)
        return text

    def inputChoice(self, question, options, hotkeys):
        root = Tk()
        #Button(root, text="Hello!").pack()
        #root.update()
        
        d = CustomMessageBox(root, question, options, hotkeys)
        root.wait_window(d.top)
        answer = d.ask()
        return answer

ui = UI()
ui.output('Test')
print ui.inputChoice('Test?', ['foo', 'bar'], ['f', 'b'])
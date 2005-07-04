import time
import re, sys, threading
import tkMessageBox, tkSimpleDialog
from Tkinter import *

class MainloopThread(threading.Thread):
    def __init__(self, window):
        threading.Thread.__init__(self)
        self.window = window

    def run(self):
        self.window.mainloop()

class CustomMessageBox(tkMessageBox.Message):
    def __init__(self, parent, question, options, hotkeys, default = None):
        self.selection = None
        self.hotkeys = hotkeys
        self.default = default

        self.top = Toplevel(parent)
        Label(self.top, text=question).grid(columnspan = 2)
        for i in range(len(options)):
            # mark hotkey with underline
            m = re.search('[%s%s]' % (hotkeys[i].lower(), hotkeys[i].upper()), options[i])
            if m:
                pos = m.start()
            else:
                options[i] += ' (%s)' % hotkeys[i]
                pos = len(options[i]) - 2
            b = Button(self.top, text = options[i], underline = pos, command = lambda h=hotkeys[i]: self.select(h))
            b.grid(row = 1, column = i)

    def select(self, i):
        self.selection = i
        self.top.destroy()

    def ask(self):
        if self.default and not self.selection:
            return self.default
        else:
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
        self.logBox.tag_config(12, foreground='red')
        self.logBox.tag_config(10, foreground='green')

        MainloopThread(self.parent).start()

    def output(self, text, urgency = 1, colors = None, newline = True):
        """
        urgency levels:
            0 - Debug output. Won't be shown in normal mode.
            1 - Will be shown in log window.
            2 - Will be shown in error box.

            TODO: introduce constants
        """
        if urgency >= 2:
            d = tkMessageBox.showinfo('title', text)
        elif urgency >= 1:
            # Save the line number before appending text
            lineCount = int(self.logBox.index(END).split('.')[0]) - 1
            self.logBox.insert(END, text)
            if colors:
                # How many characters we already added in this line
                offset = 0
                # We create a tag region for each colored character.
                # It would be more efficient to try to use longer
                # regions.
                for i in range(len(colors)):
                    if text[i] == '\n':
                        lineCount += 1
                        offset = i + 1
                    if colors[i]:
                        startidx = '%i.%i' % (lineCount, i - offset)
                        endidx = '%i.%i' % (lineCount, i + 1 - offset)
                        # tag the whole occurence (start included, stop excluded)
                        self.logBox.tag_add(colors[i], startidx , endidx)
                        
                        
            if newline:
                self.logBox.insert(END, '\n')
            # auto-scroll down
            self.logBox.see(END)

    def input(self, question):
        """
        Returns a unicode string.
        """

        answer = tkSimpleDialog.askstring('title', question)
        return answer

    def inputChoice(self, question, options, hotkeys, default = None):

        d = CustomMessageBox(self.parent, question, options, hotkeys)
        self.parent.wait_window(d.top)
        answer = d.ask()
        return answer

if __name__ == "__main__":
    ui = UI()
    ui.output('Test')
    print ui.inputChoice('Test?', ['foo', 'bar'], ['f', 'b'])

__version__ = '$Id$'

import sys; sys.path.append('..')

import config, re, sys, terminal_interface
import wx

app = wx.App()

class UI:
    def __init__(self):
        pass
    
    def output(self, text, toStdout = False):
        """
        If a character can't be displayed, it will be replaced with a
        question mark.
        """
        # comma at the end means "don't print newline"
        #print text.encode(config.console_encoding, 'replace'),
        terminal_interface.UI().output(text, toStdout)
        

    def input(self, question, password = False):
        """
        Works like raw_input(), but returns a unicode string instead of ASCII.

        Unlike raw_input, this function automatically adds a space after the
        question.
        """
        # TODO: hide input if password = True
        
        if password:
            answer = wx.PasswordEntryDialog( None, question, '','')
        else:
            answer = wx.TextEntryDialog( None, question, '', '' )
        answer.ShowModal()
        print answer.GetValue()
        #tkSimpleDialog.askstring('title', question)
        return answer.GetValue() or ''

    def inputChoice(self, question, options, hotkeys, default = None):
        goodAnswer = False
        while not goodAnswer:
            for i in range(len(options)):
                option = options[i]
                hotkey = hotkeys[i]
                m = re.search('[%s%s]' % (hotkey.lower(), hotkey.upper()), option)
                if m:
                    pos = m.start()
                    options[i] = '%s[%s]%s' % (option[:pos], option[pos], option[pos+1:])
                else:
                    options[i] = '%s [%s]' % (option, hotkey)

            prompt = '%s (%s)' % (question, ', '.join(options))
            answer = wx.TextEntryDialog(None, prompt, question, '')
            answer.ShowModal()
            answer = answer.GetValue()
            
            if answer.lower() in hotkeys or answer.upper() in hotkeys:
                return answer


if __name__ == '__main__':
    ui = UI()
    print ui.input('Test?')
app.MainLoop()


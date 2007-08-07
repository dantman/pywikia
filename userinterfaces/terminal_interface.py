
__version__ = '$Id$'

import config, transliteration
import traceback, re, sys

try:
    import ctypes
    ctypes_found = True
except ImportError:
    ctypes_found = False

# TODO: other colors:
         #0 = Black
         #1 = Blue
         #2 = Green
         #3 = Aqua
         #4 = Red
         #5 = Purple
         #6 = Yellow
         #7 = White
         #8 = Gray
         #9 = Light Blue
        #10 = Light Green
        #11 = Light Aqua
        #12 = Light Red
        #13 = Light Purple
        #14 = Light Yellow
        #15 = Bright White

unixColors = {
    #None:          chr(27) + '[0m',     # Unix end tag to switch back to default
    'lightblue':   chr(27) + '[94;1m',  # Light Blue start tag
    'lightgreen':  chr(27) + '[92;1m',  # Light Green start tag
    'lightaqua':   chr(27) + '[36;1m',  # Light Aqua start tag
    'lightred':    chr(27) + '[91;1m',  # Light Red start tag
    'lightpurple': chr(27) + '[35;1m',  # Light Purple start tag
    'lightyellow': chr(27) + '[33;1m',  # Light Yellow start tag
}

windowsColors = {
    'lightblue':   9,
    'lightgreen':  10,
    'lightaqua':   11,
    'lightred':    12,
    'lightpurple': 13,
    'lightyellow': 14,
}


startTagR = re.compile('\03{(?P<name>%s)}' % '|'.join(unixColors.keys()))
endTagR =   re.compile('\03{default}')

class UI:
    def __init__(self):
        pass

    # NOTE: We use sys.stdout.write() instead of print because print adds a
    # newline.
    
    def printColorizedInUnix(self, text, targetStream):
        lastColor = None
        for key, value in unixColors.iteritems():
            text = text.replace('\03{%s}' % key, value)
        text = text.replace('\03{default}', chr(27) + '[0m')     # Unix end tag to switch back to default
        targetStream.write(text.encode(config.console_encoding, 'replace'))

    def printColorizedInWindows(self, text, targetStream):
        """
        This only works in Python 2.5 or higher.
        """
        if ctypes_found:
            std_out_handle = ctypes.windll.kernel32.GetStdHandle(-11)
            # this relies on non-overlapping, non-cascading color tags that are all properly closed.
            # TODO: This assumption is wrong: with transliteration, there can be cascading color tags.
            startM = True
            while startM:
                startM = startTagR.search(text)
                if startM:
                    # print the text up to the tag.
                    targetStream.write(text[:startM.start()].encode(config.console_encoding, 'replace'))
                    ctypes.windll.kernel32.SetConsoleTextAttribute(std_out_handle, windowsColors[startM.group('name')])
                    # print the colored text inside the tag.
                    endM = endTagR.search(text)
                    targetStream.write(text[startM.end():endM.start()].encode(config.console_encoding, 'replace'))
                    # reset to default color
                    ctypes.windll.kernel32.SetConsoleTextAttribute(std_out_handle, config.defaultcolor)
                    text = text[endM.end():]
            # print the rest of the text
            targetStream.write(text.encode(config.console_encoding, 'replace'))
        else:
            # ctypes is only available since Python 2.5, and we won't
            # try to colorize without it. Instead we add *** after the text as a whole
            # if anything needed to be colorized.
            lines = '\n'.split(text)
            for line in lines:
                line, count = startTagR.subn('', line)
                line = endTagR.sub('', line)
                if count > 0:
                    line += '***'
                line += '\n'
                targetStream.write(line.encode(config.console_encoding, 'replace'))

    def printColorized(self, text, targetStream):
        if config.colorized_output:
            if sys.platform == 'win32':
                self.printColorizedInWindows(text, targetStream)
            else:
                self.printColorizedInUnix(text, targetStream)
        else:
            targetStream.write(text.encode(config.console_encoding, 'replace'))

    def output(self, text, newline = True, toStdout = False):
        """
        If a character can't be displayed in the encoding used by the user's
        terminal, it will be replaced with a question mark or by a
        transliteration.
        """
        if config.transliterate:
            # Encode our unicode string in the encoding used by the user's console,
            # and decode it back to unicode. Then we can see which characters
            # can't be represented in the console encoding.
            codecedText = text.encode(config.console_encoding, 'replace').decode(config.console_encoding)
            transliteratedText = ''
            # A transliteration replacement might be longer than the original
            # character, e.g. ? is transliterated to ch.
            # We need to reflect this growth in size by shifting the color list
            # entries. This variable counts how much the size has grown.
            sizeIncrease = 0
            prev = "-"
            for i in xrange(len(codecedText)):
                # work on characters that couldn't be encoded, but not on
                # original question marks.
                if codecedText[i] == '?' and text[i] != u'?':
                    try:
                        transliterated = transliteration.trans(text[i], default = '?', prev = prev, next = text[i+1])
                    except IndexError:
                        transliterated = transliteration.trans(text[i], default = '?', prev = prev, next = ' ')
                    # transliteration was successful. The replacement
                    # could consist of multiple letters.
                    # mark the transliterated letters in yellow.
                    transliteratedText += '\03{lightyellow}%s\03{default}' % transliterated
                    transLength = len(transliterated)
                    # memorize if we replaced a single letter by multiple letters.
                    sizeIncrease += transLength - 1 + len('\03{lightyellow}\03{default}')
                    if len(transliterated) > 0:
                        prev = transliterated[-1]
                else:
                    # no need to try to transliterate.
                    transliteratedText += codecedText[i]
                    prev = codecedText[i]
            text = transliteratedText
        if newline:
            text += u'\n'

        if toStdout:
            targetStream = sys.stdout
        else:
            targetStream = sys.stderr
        self.printColorized(text, targetStream)

    def input(self, question, password = False):
        """
        Works like raw_input(), but returns a unicode string instead of ASCII.

        Unlike raw_input, this function automatically adds a space after the
        question.
        """

        # sound the terminal bell to notify the user
        if config.ring_bell:
            sys.stdout.write('\07')
        self.output(question + ' ', newline = False)
        if password:
            import getpass
            text = getpass.getpass('')
        else:
            text = raw_input()
        text = unicode(text, config.console_encoding)
        return text

    def inputChoice(self, question, options, hotkeys, default = None):
        for i in range(len(options)):
            option = options[i]
            hotkey = hotkeys[i]
            # try to mark a part of the option name as the hotkey
            m = re.search('[%s%s]' % (hotkey.lower(), hotkey.upper()), option)
            if hotkey == default:
                caseHotkey = hotkey.upper()
            else:
                caseHotkey = hotkey
            if m:
                pos = m.start()
                options[i] = '%s[%s]%s' % (option[:pos], caseHotkey, option[pos+1:])
            else:
                options[i] = '%s [%s]' % (option, caseHotkey)
        # loop until the user entered a valid choice
        while True:
            prompt = '%s (%s)' % (question, ', '.join(options))
            answer = self.input(prompt)
            if answer.lower() in hotkeys or answer.upper() in hotkeys:
                return answer
            elif default and answer=='':		# empty string entered
                return default

    def editText(self, text, jumpIndex = None, highlight = None):
        """
        Uses a Tkinter edit box because we don't have a console editor
        
        Parameters:
            * text      - a Unicode string
            * jumpIndex - an integer: position at which to put the caret
            * highlight - a substring; each occurence will be highlighted
        """
        try:
            import gui
        except ImportError, e:
            print 'Could not load GUI modules: %s' % e
            return text
        editor = gui.EditBoxWindow()
        return editor.edit(text, jumpIndex = jumpIndex, highlight = highlight)

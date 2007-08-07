import sys

class UI:
    def __init__(self):
        pass

    def output(self, text, newline = True, toStdout = False):
        # all debug output etc. will be ignored.
        if toStdout:
            sys.stdout.write(text.encode('UTF-8', 'replace'))
    
    def input(self, question, password = False):
        # CGI is output-only.
        self.output(question + ' ', newline = False, toStdout = True)

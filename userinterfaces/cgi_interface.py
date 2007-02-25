import sys

class UI:
    def __init__(self):
        pass

    def output(self, text, colors = None, newline = True, showcgi = False):
        if not showcgi:
            return
        sys.stdout.write(text.encode('UTF-8', 'replace'))
    
    def input(self, question, colors = None):
        self.output(question + ' ', newline = False, showcgi = True)

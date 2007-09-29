# Helper script for delinker and image_replacer

__version__ = '$Id$'

import sys
sys.path.append('commonsdelinker')

module = 'delinker'
if len(sys.argv) > 1:
	if sys.argv[1] == 'replacer':
		del sys.argv[1]
		module = 'image_replacer'

__import__(module, locals = {'__name__': '__main__'})
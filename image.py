# -*- coding: utf-8 -*-
"""
This script can be used to change one image to another or remove an image entirely.

Syntax: python image.py image_name [new_image_name]

If only one command-line parameter is provided then that image will be removed; if
two are provided, then the first image will be replaced by the second one on all pages.

Command line options:

-summary:  Provide a custom edit summary.  If the summary includes spaces, surround
           it with single quotes, such as:  -summary:'My edit summary'
-always    Don't prompt to make changes, just do them.
-loose     Do loose replacements.  This will replace all occurences of the name of the
           image (and not just explicit image syntax).  This should work to catch all
           instances of the image, including where it is used as a template parameter
           or in image galleries.  However, it can also make more mistakes.  This only
           works with image replacement, not image removal.

Examples:

The image "FlagrantCopyvio.jpg" is about to be deleted, so let's first remove it from
everything that displays it:

    python image.py FlagrantCopyvio.jpg

The image "Flag.svg" has been uploaded, making the old "Flag.jpg" obselete:

    python image.py Flag.jpg Flag.svg

"""
#
# Distributed under the terms of the MIT license.
#
import wikipedia, config
import replace, pagegenerators
import re, sys, string

class ImageRobot:
    """
    This robot will load all pages yielded by a file links image page generator and
    replace or remove all occurences of the old image.
    """
    # Summary messages for replacing images
    msg_replace={
        'de': u'Bot: Ersetze Bild %s durch %s',
        'en': u'Robot - Replacing image %s with %s',
        'fr': u'Bot: Remplace image %s par %s',
        'he': u'רובוט - מחליף את התמונה %s בתמונה %s',
        'lt': u'robotas: vaizdas %s keičiamas į %s',
        'pt': u'Bot: Alterando imagem %s para %s',
    }

    # Summary messages for removing images
    msg_remove={
        'de': u'Bot: Entferne Bild %s',
        'en': u'Robot - Removing image %s',
        'fr': u'Bot: Enleve image %s',
        'he': u'רובוט - מסיר את התמונה %s',
        'lt': u'robotas: Šalinamas vaizdas %s',
        'pt': u'Bot: Alterando imagem %s',
    }

    def __init__(self, generator, oldImage, newImage = None, summary = '', always = False, loose = False):
        """
        Arguments:
            * generator - A page generator.
            * oldImage  - The title of the old image (without namespace)
            * newImage  - The title of the new image (without namespace), or
                          None if you want to remove the image.
        """
        self.generator = generator
        self.oldImage = oldImage
        self.newImage = newImage
        self.summary = summary
        self.always = always
        self.loose = loose

        # get edit summary message
        mysite = wikipedia.getSite()
        if summary:
            wikipedia.setAction(summary)
        elif self.newImage:
            wikipedia.setAction(wikipedia.translate(mysite, self.msg_replace) % (self.oldImage, self.newImage))
        else:
            wikipedia.setAction(wikipedia.translate(mysite, self.msg_remove) % self.oldImage)

    def run(self):
        """
        Starts the robot's action.
        """
        # regular expression to find the original template.
        # {{vfd}} does the same thing as {{Vfd}}, so both will be found.
        # The old syntax, {{msg:vfd}}, will also be found.
        # The group 'parameters' will either match the parameters, or an
        # empty string if there are none.

        replacements = []

        if not wikipedia.getSite().nocapitalize:
            old = '[' + self.oldImage[0].upper() + self.oldImage[0].lower() + ']' + self.oldImage[1:]
        else:
            old = self.oldImage

        old = re.sub('[_ ]', '[_ ]', old)
        #TODO: Add internationalization of Image namespace name.
        if not self.loose or not self.newImage:
            ImageRegex = re.compile(r'\[\[ *[Ii]mage:' + old + ' *(?P<parameters>\|[^\n]+|) *\]\]')
        else:
            ImageRegex = re.compile(r'' + old)

        if self.newImage:
            if not self.loose:
                replacements.append((ImageRegex, '[[Image:' + self.newImage + '\g<parameters>]]'))
            else:
                replacements.append((ImageRegex, self.newImage))
        else:
            replacements.append((ImageRegex, ''))

        #Note that the [] parameter here is for exceptions (see replace.py).  For now we don't use it.
        replaceBot = replace.ReplaceRobot(self.generator, replacements, [], self.always)
        replaceBot.run()
    
def main():
    oldImage = None
    newImage = None
    summary = ''
    always = False
    loose = False
    # read command line parameters
    for arg in wikipedia.handleArgs():
        if arg == '-always':
            always = True
        elif arg == '-loose':
            loose = True
        elif arg.startswith('-summary'):
            if len(arg) == len('-summary'):
                summary = wikipedia.input(u'Choose an edit summary: ')
            else:
                summary = arg[len('-summary:'):]
        else:
            if oldImage:
                newImage = arg
            else:
                oldImage = arg

    if not oldImage:
        wikipedia.showHelp('image')
    else:
        mysite = wikipedia.getSite()
        ns = mysite.image_namespace()

        oldImagePage = wikipedia.Page(mysite, ns + ':' + oldImage)

        gen = pagegenerators.FileLinksGenerator(oldImagePage)
        preloadingGen = pagegenerators.PreloadingGenerator(gen)

        bot = ImageRobot(preloadingGen, oldImage, newImage, summary, always, loose)
        bot.run()

if __name__ == "__main__":
    try:
        main()
    finally:
        wikipedia.stopme()

# -*- coding: utf-8 -*-
"""
This script processes the Categories for discussion working page.  It parses
out the actions that need to be taken as a result of CFD discussions (as posted
to the working page by an administrator) and performs them.

Syntax: python cfd.py

"""

# (C) Ben McIlwain, 2008
#
# Distributed under the terms of the MIT license.

import wikipedia
import re
import category

# Regular expression declarations
# See the en-wiki CFD working page at [[Wikipedia:Categories for discussion/Working]]
# to see how these work in context.  To get this bot working on other wikis you will
# need to adjust these regular expressions at the very least.
nobots = re.compile(r"NO\s*BOTS", re.IGNORECASE);
example = re.compile(r"\[\[\:Category\:(.)\1\1\1\1\]\]", re.IGNORECASE);
speedymode = re.compile(r"^===*\s*Speedy Moves\s*===*\s*$", re.IGNORECASE);
movemode = re.compile(r"^===*\s*Move\/Merge then delete\s*===*\s*$", re.IGNORECASE);
emptymode = re.compile(r"^===*\s*Empty then delete\s*===*\s*$", re.IGNORECASE)
deletemode = re.compile(r"^===*\s*Ready for deletion\s*===*\s*$", re.IGNORECASE)
maintenance = re.compile(r"^===*\s*Old by month categories with entries\s*===*\s*$", re.IGNORECASE)
dateheader = re.compile(r"(\[\[Wikipedia\:Categories[_ ]for[_ ](?:discussion|deletion)\/Log\/([^\]]*?)\]\])", re.IGNORECASE)
movecat = re.compile(r"\[\[\:Category\:([^\]]*?)\]\][^\]]*?\[\[\:Category\:([^\]]*?)\]\]", re.IGNORECASE)
deletecat = re.compile(r"\[\[\:Category\:([^\]]*?)\]\]", re.IGNORECASE)
findday = re.compile(r"\[\[(Wikipedia\:Categories for (?:discussion|deletion)\/Log\/\d{4} \w+ \d+)#", re.IGNORECASE)

class ReCheck:
    def __init__(self):
        self.result = None
    def check(self, pattern, text):
        self.result = pattern.search(text)
        return self.result

def main():
    wikipedia.handleArgs();

    page = wikipedia.Page(wikipedia.getSite(), 'Wikipedia:Categories for discussion/Working')

    # Variable declarations
    day = "None"
    mode = "None"
    src = "None"
    dest = "None"
    line = ""
    summary = ""
    robot = None

    m = ReCheck()
    for line in page.get().split("\n"):
        if (nobots.search(line)):
            # NO BOTS!!!
            pass
        elif (example.search(line)):
            # Example line
            pass
        elif (speedymode.search(line)):
            mode = "Speedy"
            day = "None"
        elif (movemode.search(line)):
            mode = "Move"
            day = "None"
        elif (emptymode.search(line)):
            mode = "Empty"
            day = "None"
        elif (deletemode.search(line)):
            mode = "Delete"
            day = "None"
        elif (maintenance.search(line)):
            # It's probably best not to try to handle these in an automated fashion.
            mode = "None"
            day = "None"
        elif (m.check(dateheader, line)):
            day = m.result.group(1)
        elif (m.check(movecat, line)):
            src = m.result.group(1)
            dest = m.result.group(2)
            if (mode == "Move" and day != "None"):
                summary = "Robot - Moving category " + src + " to " + dest + " per [[WP:CFD|CFD]] at " + findDay(src, day) + "."
            elif (mode == "Speedy"):
                summary = "Robot - Speedily moving category " + src + " to " + dest + " per [[WP:CFD|CFD]]."
            else:
                continue
            robot = category.CategoryMoveRobot(oldCatTitle=src, newCatTitle=dest, batchMode=True,
                                      editSummary=summary, inPlace=True, moveCatPage=True,
                                      deleteEmptySourceCat=True)
        elif (m.check(deletecat, line)):
            src = m.result.group(1)
            # I currently don't see any reason to handle these two cases separately, though
            # if are guaranteed that the category in the "Delete" case is empty, it might be
            # easier to call delete.py on it.
            if ((mode == "Empty" or mode == "Delete") and day != "None"):
                summary = "Robot - Removing category " + src + " per [[WP:CFD|CFD]] at " + findDay(src, day) + "."
            else:
                continue
            robot = category.CategoryRemoveRobot(catTitle=src, batchMode=True, editSummary=summary,
                                                 useSummaryForDeletion=True, inPlace=True)
        else:
            # This line does not fit any of our regular expressions, so ignore it.
            pass
        if (summary != "" and robot != None):
            wikipedia.output(summary, toStdout=True)
            # Run, robot, run!
            robot.run()
        summary = ""
        robot = None

# This function grabs the wiki source of a category page and attempts to
# extract a link to the CFD per-day discussion page from the CFD template.
# If the CFD template is not there, it will return the value of the second
# parameter, which is essentially a fallback that is extracted from the
# per-day subheadings on the working page.
def findDay(pageTitle, oldDay):
    page = wikipedia.Page(wikipedia.getSite(), "Category:" + pageTitle)
    try:
        pageSrc = page.get()
        m = findday.search(pageSrc)
    except wikipedia.NoPage:
        m = None

    if (m != None):
        return "[[" + m.group(1) + "]]"
    else:
        wikipedia.output("Could not find CFD day link on Category:" + pageTitle + "\n", toStdout=True)
        return oldDay

if __name__ == "__main__":
    try:
        main()
    except:
        wikipedia.stopme()
        raise
    else:
        wikipedia.stopme()


#coding: iso-8859-1
"""
Check pages on the English Wikipedia whether they are in the form
Something, State, and if so, create a redirect from Something, ST.

Arguments understood by various bots:
-lang: Choose your language - however, this bot probably is only
       to be used on en:
-putthrottle: Specify minimum number of seconds to wait between
              edits

Specific arguments:
-start:xxx Specify the place in the alphabet to start searching
-force: Don't ask whether to create pages, just create them.

"""
#
# (C) Andre Engels, 2004
#
# Distribute under the terms of the PSF license.
#

import re,wikipedia,sys

start = '0'
force = False
msg = {'en':'Creating state abbreviation redirect'
       }

abbrev = {
    'Alabama': 'AL',
    'Alaska': 'AK',
    'Arizona': 'AZ',
    'Arkansas': 'AR',
    'California': 'CA',
    'Colorado': 'CO',
    'Delaware': 'DE',
    'Florida': 'FL',
    'Georgia': 'GA',
    'Hawaii': 'HI',
    'Idaho': 'ID',
    'Illinois': 'IL',
    'Indiana': 'IN',
    'Iowa': 'IA',
    'Kansas': 'KS',
    'Kentucky': 'KY',
    'Louisiana': 'LA',
    'Maine': 'ME',
    'Maryland': 'MD',
    'Massachusetts': 'MA',
    'Michigan': 'MI',
    'Minnesota': 'MN',
    'Mississippi': 'MS',
    'Missouri': 'MO',
    'Montana': 'MT',
    'North Carolina': 'NC',
    'North Dakota': 'ND',
    'Nebraska': 'NE',
    'Nevada': 'NV',
    'New Hampshire': 'NH',
    'New Jersey': 'NJ',
    'New Mexico': 'NM',
    'New York': 'NY',
    'Ohio': 'OH',
    'Oklahoma': 'OK',
    'Oregon': 'OR',
    'Pennsylvania': 'PA',
    'Rhode Island': 'RI',
    'South Carolina': 'SC',
    'South Dakota': 'SD',
    'Tennessee': 'TN',
    'Texas': 'TX',
    'Utah': 'UT',
    'Vermont': 'VT',
    'Virginia': 'VA',
    'Washington': 'WA',
    'West Virginia': 'WV',
    'Wisconsin': 'WI',
    'Wyoming': 'WY'
    }

for arg in sys.argv[1:]:
    if wikipedia.argHandler(arg):
        pass
    elif arg.startswith('-start:'):
        start = arg[7:]
    elif arg == '-force':
        force = True
    else:
        print('Warning: argument "%s" not understood; ignoring.')%arg

for p in wikipedia.allpages(start = start):
    for sn in abbrev:
        R=re.compile('[^[]]*' + '\%2C_' + sn)
        for res in R.findall(p.urlname()):
            pl=wikipedia.PageLink(wikipedia.mylang,p.urlname().replace(sn,abbrev[sn]))
            # A bit hacking here - the real work is done in the 'except wikipedia.NoPage'
            # part rather than the 'try'.
            try:
                goal = pl.getRedirectTo()
                if wikipedia.PageLink(wikipedia.mylang, goal):
                    print("Not creating %s - redirect already exists.") % goal
                else:
                    print("WARNING!!! %s already exists but redirects elsewhere!") % goal
            except wikipedia.IsNotRedirectPage:
                print("WARNING!!! Page %s already exists and is not a redirect. Please check page!") % goal
            except wikipedia.NoPage:
                change=''
                if p.isRedirectPage():
                    p2 = wikipedia.PageLink(wikipedia.mylang, p.getRedirectTo())
                    print ('Note: goal page is redirect. Creating redirect to "%s" to avoid double redirect.')%p2.urlname().replace("%2C",",").replace("_"," ")
                else:
                    p2 = p
                if force:
                    change='y'
                else:
                    while not change in ['y','n']:
                        print ("Create redirect %s")%pl.urlname().replace("%2C",",").replace("_"," ")
                        change = raw_input("(y/n)? ")
                if change=='y':
                    text = '#REDIRECT [['+p2.urlname().replace("%2C",",").replace("_"," ")+']]'
                    pl.put(text, comment=msg[wikipedia.chooselang(wikipedia.mylang,msg)], minorEdit = '0')

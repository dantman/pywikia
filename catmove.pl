#!/usr/bin/perl

#This Perl script takes a list of category moves to make and uses category.py to make them.
#The input format is as follows:
#    # Category:US to Category:United States
#Just copy-paste the list of categories to move from the Wiki, put them in a text-file, and
#redirect to stdin, i.e., perl catmove.pl < catmoves.txt
#
#Note that error-handling isn't nearly as good as it could be (this script is only 13 lines
#long after all!).

while (<STDIN>) {
    if ($_ =~ m/^\s*\#?\s*Category:(.*?)\s*to\s*Category:(.*?)\s*$/) {
	print "Now executing: python category.py move -batch -from:\'$1\' -to:\'$2\'\n";
	system("python category.py move -batch -from:\'$1\' -to:\'$2\'");
	if ( $? != 0) {
	    print "Error or interrupted, program aborting.\n";
	    exit 1;
	}
    }
    else {
	print "Invalid line: $_\n";
    }
}

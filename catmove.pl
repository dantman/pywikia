#!/usr/bin/perl

# This Perl script takes a list of category moves or removes to make and uses category.py.
# The input format is as follows:
#    * Category:US to Category:United States
#  OR
#    * Category:US
# Just copy-paste the list of categories to move or remove from the Wiki, put them in a
# text-file, and redirect to stdin, i.e., perl catmove.pl < catmoves.txt
# If you want to use an edit summary, then pass it in as a parameter, i.e.,
# perl catmove.pl "Emptying dead category" < catmoves.txt
# Note that if your summary has multiple words in it then enclose it in quotes.
# 
# To set edit summaries, you can also preface a line with a semicolon ;
# That will be the edit summary for all subsequent executions ... unless you modify the
# edit summary again with another semicolon.  In this way you can take care of many days
# worth of WP:CFD backlog with a single execution.

my $editSummary = '';
my $customSummary = 0;
if ($#ARGV >= 0) {
    $customSummary = 1;
    $editSummary = shift;
}

while (<STDIN>) {
    #Move articles from one category to another.
    if ($_ =~ m/^\s*[\#\*]?\s*Category:(.*?)\s*to\s*Category:(.*?)\s*$/) {
	my $from = $1;
	my $to = $2;
	if ($customSummary == 0) {
	    print "Now executing: python category.py move -batch -from:\"$from\" -to:\"$to\"\n";
	    system("python category.py move -batch -from:\"$from\" -to:\"$to\"");
	}
	else {
	    print "Now executing: python category.py move -batch -from:\"$from\" -to:\"$to\" -summary:\"$editSummary\"\n";
	    system("python category.py move -batch -from:\"$from\" -to:\"$to\" -summary:\"$editSummary\"");
	}
	if ( $? != 0) {
	    print "Error or interrupted, program aborting.\n";
	    exit 1;
	}
    }
    #Empty out a category.
    elsif ($_ =~ m/^\s*[\#\*]?\s*Category:(.*?)\s*$/) {
	my $from = $1;
	if ($customSummary == 0) {
	    print "Now executing: python category.py remove -batch -from:\"$from\"\n";
	    system("python category.py remove -batch -from:\"$from\"");
	}
	else {
	    print "Now executing: python category.py remove -batch -from:\"$from\" -summary:\"$editSummary\"\n";
	    system("python category.py remove -batch -from:\"$from\" -summary:\"$editSummary\"");
	}
	if ( $? != 0) {
	    print "Error or interrupted, program aborting.\n";
	    exit 1;
	}
    }	
    elsif ($_ =~ m/^\s*;\s*(.*)\s*$/) {
	$customSummary = 1;
	$editSummary = $1;
    }
    else {
	print "Invalid line: $_\n";
    }
}

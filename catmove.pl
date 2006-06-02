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

#Necessary for thread handling.
use POSIX ":sys_wait_h";

#Preliminary setup.
my $editSummary = '';
my $customSummary = 0;
my $throttle = 6;
my $sysCall = '';
if ($#ARGV >= 0) {
    $customSummary = 1;
    $editSummary = shift;
}

#Loop through all standard input.
while (<STDIN>) {
    #Matches category moves and category removals.
    if ($_ =~ m/^\s*[\#\*]?\s*[Cc]ategory:(.*?)\s*to\s*[Cc]ategory:(.*?)\s*$/ || $_ =~ m/^\s*[\#\*]?\s*[Cc]ategory:(.*?)\s*$/) {
	#Matches category moves.
	if ($_ =~ m/^\s*[\#\*]?\s*[Cc]ategory:(.*?)\s*to\s*[Cc]ategory:(.*?)\s*$/) {
	    my $from = $1;
	    my $to = $2;
	    if ($customSummary == 0) {
		$sysCall = "python category.py move -batch -from:\"$from\" -to:\"$to\" -putthrottle:$throttle";
	    } else {
		$sysCall = "python category.py move -batch -from:\"$from\" -to:\"$to\" -summary:\"$editSummary\" -putthrottle:$throttle";
	    }
	}
	#Matches category removals.
	elsif ($_ =~ m/^\s*[\#\*]?\s*[Cc]ategory:(.*?)\s*$/) {
	    my $from = $1;
	    if ($customSummary == 0) {
		$sysCall = "python category.py remove -batch -from:\"$from\" -putthrottle:$throttle";
	    } else {
		$sysCall = "python category.py remove -batch -from:\"$from\" -summary:\"$editSummary\" -putthrottle:$throttle";
	    }
	}

	#Fork off the execution of the Python bot as its own thread.  Errors will be skipped and execution continues
	#through the whole list.  Ctrl-C will quit everything immediately, though.  (This is why we can't use the
	#much simpler system() function).
	print "Executing: $sysCall\n";
	defined (my $pid = fork) or die "Cannot fork: $!";
	unless ($pid) {
	    exec($sysCall);
	}
	#If the Python script terminates abnormally print something to that effect.
	if (waitpid($pid, 0) == 256) {
	    print "Error, python script terminated abnormally.\n";
	}
    }
    #Setting the edit summary.
    elsif ($_ =~ m/^\s*;\s*(.*)\s*$/) {
	$customSummary = 1;
	$editSummary = $1;
    } else {
	print "Invalid line: $_\n";
    }
}

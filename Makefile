all:
	/bin/true

distrib:
	/bin/rm -rf pywikipediabot
	mkdir pywikipediabot
	cp *.py CONTENTS *-exceptions.dat pywikipediabot
	/bin/rm -f $(HOME)/robot.zip
	zip -rv $(HOME)/robot.zip pywikipediabot/*
	tar -cvzf $(HOME)/robot.tar.gz pywikipediabot/*

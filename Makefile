all:
	/bin/true

distrib:
	/bin/rm -rf pywikipediabot
	mkdir pywikipediabot
	cp *.py CONTENTS *-exceptions.dat pywikipediabot
	rm $(HOME)/robot.zip
	zip -rv $(HOME)/robot.zip pywikipediabot/*
	tar -cvzf $(HOME)/robot.tar.gz pywikipediabot/*

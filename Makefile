all:
	/bin/true

distrib:
	/bin/rm -r robot
	mkdir robot
	cp *.py CONTENTS nl-exceptions.dat robot
	rm $(HOME)/robot.zip
	zip -rv $(HOME)/robot.zip robot/*

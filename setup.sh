#!/bin/bash

# Install python-pip git base-devel asciidoc

cd web/aiweb_tools/isolate
make
sudo chown root isolate
sudo chmod u+s isolate
cd ../../..

pip3 install django django-registration-redux cloudpickle skills

for f in compiled lock maps matchmaker results runner submissions tasks worker temp maps/Ants maps/Tron
do
	if [ ! -e "$f" ]
	then
		mkdir "$f"
		if [ "$f" == maps/Ants ]
		then
			unzip -d maps/Ants/ resources/ants-maps.zip 
		fi
		if [ "$f" == maps/Tron ]
		then
			unzip -d maps/Tron/ resources/tron-maps.zip 
		fi
	fi
done

#!/bin/bash

CSVFILESDIR="../../files/csv/"

FILES20=$(ls $CSVFILESDIR | sort -R | head -20)
for LINE in $FILES20
do
	echo "$CSVFILESDIR$LINE"
	head -10 "$CSVFILESDIR$LINE"
	echo ""
	echo ""
	echo ""
done

#!/bin/bash

<<EXECUTE
./t7.sh /usr/share README
EXECUTE

##############################################################################################

where_to_search=$1
what_to_search=$2

# -R tells command ls to list recursively
list=$(ls -R $where_to_search)

counting=0

while read items
do

if [[ $items =~ "$what_to_search"$ ]]
then
((counting+=1))
fi

done <<< "$list"

echo "Total number of pure README is: $counting"

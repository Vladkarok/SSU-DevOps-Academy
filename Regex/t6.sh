#!/bin/bash
<< HOWTOEXECUTE
./t6.sh /etc/group daemon
HOWTOEXECUTE

where_to_search=$1
what_to_search="^($2)"



#############################################################################################################################################
# REGEX IN BASH SCRIPT

# Declare counting variable
summ=0

# Read items from specified file $where_to_search inserted in "done <" section
 while read line_read; do

    # Conditional operator IF with regex comparing "=~"
     if [[ ! $line_read =~ $what_to_search ]]
     then

         # Printing
         echo $line_read

         # Increment counter by one for each regex complition
         ((summ+=1))

    # End of IF conditions    
     fi

# Inserting file
 done < $where_to_search

 # Printing total number and what we searched
echo -e "\nTotal number of hitted pattern without $2 is $summ"


<< COMMENT
< is process substitution feeds the output of a process (or processes) into the stdin of another process.

<< is known as HERE-DOCUMENT structure. You let the program know what will be the ending text,
 and whenever that delimiter is seen, the program will read all the stuff you've given to the program as input and perform a task upon it.

<<< is known as HERE-STRING. Instead of typing in text, you give a pre-made string of text to a program.
COMMENT


#!/bin/bash
<< EXP
-cmin n
File's status was last changed n minutes ago.

-maxdepth levels
Descend at most levels (a non-negative integer) levels of directories below the command line arguments.

-type c
File is of type c:
    f - regular file

EXP

echo "Input directory"

read directory

echo "Input time in minutes"

read minutes

files=$(find $directory . -maxdepth 1 -type f -cmin -$minutes)

echo -e "\nFiles in $directory that was modified less than $minutes minutes ago are:\n $files"
#!/bin/bash
#Usage: Read from excel, find author of specified line, export result to text
# Author: Damon Otero
# ---------------------------------------------------------------------------


#repo='path/to/repo'
repo=$1
#file='path/to/file'
file=$2
#line number of file
line=$3
# error type is vuln or bug?
errtype=$4
# description of flaw
desc=$5
# name of output file
output=$6

author=`git -C $repo blame -L $line,$line --format='%ae' --porcelain $file | grep 'author ' | sed 's/author //' | sed 's/ /_/g'`
shortpath=`echo $file | sed 's/^.*\(final*\)/\1/g' | sed 's/final//g'`
echo $author
echo $shortpath

echo $author '	' $shortpath '	' $errtype '	' $line '	' $desc >> $output

#!/bin/bash

# Rough estimate of difference in numerical results of different sovlers
# might need future parsing fixes for newly added adapters (awk will complain when this happen)
# 
# Input: folder where results should be compared and 
# (optional) maximum relative difference between
# difference numerical values in the files ( averaged over the file and over the individual field)

avg_diff_limit="0.01"
max_diff_limit="0.01"

if [ $# -lt 2 ]; then
  echo 1>&2 "Usage: $0 folder1 folder2"
  exit 1
else
  folder1=$1
  folder2=$2
  shift
  shift
fi

for i in "$@"; 
do case $i in
    --avg_diff=*)
    avg_diff_limit="${i#*=}"
    ;;
    --max_diff=*)
    max_diff_limit="${i#*=}"
    ;;
    *)
    echo "Uknown options $i. Possible options: --avg_diff, --max_diff "; exit 1;;
esac
done

# Get the list of files that differ
diff_result=$( diff -rq $folder1 $folder2 )

# split result into two, depending whether files are unique in one folder
# or just differ
diff_files=$( echo "$diff_result" | sed '/Only/d' )
only_files=$( echo "$diff_result" | sed '/differ/d')

# Pairwise compare files
if [ -n "$diff_files" ]; then
  mapfile -t array_files < <( echo "$diff_files"  | sed 's/Files\|and\|differ//g' )
  arr_len="${#array_files[@]}"

  for (( i = 0; i<${arr_len}; i = i + 1));
  do
    file1=$( echo "${array_files[i]}" | awk '{print $1}' )
    file2=$( echo "${array_files[i]}" | awk '{print $2}' )
    rawdiff=$( diff -y --speed-large-files --suppress-common-lines "$file1" "$file2" )
    # Filter output files, ignore lines with words (probably not the results)
    # removes |<>() characters
    # Do not delete "e", since it can be used as exponent
    filtered_diff=$( echo "$rawdiff" | sed 's/(\|)\||\|>\|<//g; /[a-df-zA-Z]\|Version/d' )

    # Paiwise compares files fields, that are produces from diffs and computes average and maximum
    # relative differences
    if [ -n "$filtered_diff" ]; then
      rel_max_difference=$( echo "$filtered_diff" | awk 'function abs(v) {return v < 0 ? -v : v} { radius=NF/2;
              max_diff=0;
              for(i = 1; i <= radius; i++) {
              if ($i != 0) {
                ind_diff= abs((($(i + radius)-$i)/$i ));
                sum += ind_diff;
                if  (ind_diff > max_diff )  { max_diff = ind_diff }
              }
             }
             } END { diff=sum/( NR*radius ); if (diff > ENVIRON["avg_diff_limit"] || max_diff > ENVIRON["max_diff_limit"])  { print diff, max_diff }}')
  fi

    if [ -n "$rel_max_difference" ]; then
      # Split by space and transform into the array
      difference=( $rel_max_difference )
      echo "Difference between numerical fields in $file1 and $file2 -  Average: ${difference[0]}. Maximum: ${difference[1]}"
      diff -yr --suppress-common-lines $folder1 $folder2
    fi
  done
fi

# Files that are present only in one system
if [ -n "$only_files" ]; then
  echo "$only_files"
fi

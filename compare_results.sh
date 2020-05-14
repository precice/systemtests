#!/bin/bash

# Roughly compares difference in numerical results between different adapter runs.
# The values should not be completely different, but might vary in non-significant digits
# due to FP on different architectures/OS.
#
# It just strips away all "non-numerical" looking data and then compares files field by field.
# Might need future parsing fixes for newly added adapters (awk will complain when this happen)
#
# Input: folder where results should be compared and (optional) maximum relative difference between
# numerical values in the reference and obtained files ( averaged over the file and over the individual field)

avg_diff_limit="0.001"
max_diff_limit="0.001"


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
    echo "Unknown options $i. Possible options: --avg_diff, --max_diff "; exit 1;;
esac
done

ret=0

# Get the list of files that differ
diff_result=$( diff -rq $folder1 $folder2 )

# split result into two, depending whether files are unique in one folder
# or just differ
diff_files=$( echo "$diff_result" | sed '/Only/d' )
only_files=$( echo "$diff_result" | sed '/differ/d')


echo "------------- Comparing files -------------"

# Pairwise compare files
if [ -n "$diff_files" ]; then
  mapfile -t array_files < <( echo "$diff_files"  | sed 's/Files\|and\|differ//g' )
  arr_len="${#array_files[@]}"

  # loop through differing files
  for (( i = 0; i<${arr_len}; i = i + 1));
  do
    file1=$( echo "${array_files[i]}" | awk '{print $1}' )
    file2=$( echo "${array_files[i]}" | awk '{print $2}' )

    # Filter output files, ignore lines with words (probably not the results)
    # Do not delete "e", since it can be used as exponent
    # removes |<>() characters
    num_filter='s/(\|)\||\|>\|<//g; /[a-df-zA-Z]\|[vV]ersion/d'
    # Filter for text lines. Compare these seperately from numerical lines
    # Ignore any timestamps
    txt_filter='s/(\|)\||\|>\|<//g; /[a-df-zA-Z]\|[vV]ersion/!d; s/[0-9][0-9]:[0-9][0-9]:[0-9][0-9]//g; /Timestamp\|[rR]untime\|Unexpected end of/d; /Run finished/q'
    file1_num=$( cat "$file1" | sed "$num_filter")
    file2_num=$( cat "$file2" | sed "$num_filter")

    file1_txt=$( cat "$file1" | sed "$txt_filter")
    file2_txt=$( cat "$file2" | sed "$txt_filter")


    num_diff=$( diff -y --speed-large-files --suppress-common-lines <(echo "$file1_num") <(echo "$file2_num") )
    txt_diff=$( diff -y --speed-large-files --suppress-common-lines <(echo "$file1_txt") <(echo "$file2_txt") )


    # Pairwise compares files fields, that are produces from diffs and computes average and maximum
    # relative differences
    filename=$(basename $file1) # total file paths are pretty long, this keep info concise
    echo "Comparing values in '$filename'..."
    if [ -n "$num_diff" ]; then
      rel_max_difference=$( export max_diff_limit; export avg_diff_limit; echo "$num_diff" | awk 'function abs(v) {return v < 0 ? -v : v} { radius=NF/2;
              max_diff=0;
              sum=0;
              for(i = 1; i <= radius; i++) {
              if ($i != 0) {
                ind_diff= abs((($(i + radius)-$i)/$i ));
                sum += ind_diff;
                if  (ind_diff > max_diff )  { max_diff = ind_diff }
              }
             }
             } END { diff=2*sum/( NR*NF ); if (diff > ENVIRON["avg_diff_limit"] || max_diff > ENVIRON["max_diff_limit"])  { print diff, max_diff }}')
    fi

    if [ -n "$rel_max_difference" ]; then
      # Split by space and transform into the array
      difference=( $rel_max_difference )
      echo -e "> Numerical difference in $file1 and $file2"
      echo -e "$num_diff"
      echo -e "Average: ${difference[0]} ; Maximum: ${difference[1]} ${NC}"
      ret=1
    fi
    if [ -n "$txt_diff" ]; then
      echo -e "> Text difference in $file1 and $file2"
      echo -e "$txt_diff"
      ret=1
    fi
  done
fi

# Files that are present only in reference or output folder
if [ -n "$only_files" ]; then
  echo -e "> $only_files"
  ret=1
fi
echo "----------- Comparison finished -----------"

exit $ret

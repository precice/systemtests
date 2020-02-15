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
      rel_max_difference=$( export max_diff_limit; export avg_diff_limit;
          echo "$filtered_diff" | awk 'function abs(v) {return v < 0 ? -v : v}
          {
            radius=NF/2;
            max_diff=0;
            sum=0;
            if ( NR*NF <= 0 ) {
              printf("%s:%d: invalid value: NR*NF <= 0, compared files are invalid!",FILENAME,FNR) > "/dev/stderr";
              _invalid_value_ = 1
            }
            for(i = 1; i <= radius; i++) {
              if ($i != 0) {
                ind_diff= abs((($(i + radius)-$i)/$i ));
                sum += ind_diff;
                if  (ind_diff > max_diff )  { max_diff = ind_diff }
              }
            }
          }
          END {
            if (_invalid_value_) {
              exit 1;
            }
            diff=2*sum/( NR*NF );
            if (diff > ENVIRON["avg_diff_limit"] || max_diff > ENVIRON["max_diff_limit"]) {
              print diff, max_diff
            }
          }' )
    fi

    if [ -n "$rel_max_difference" ]; then
      # Split by space and transform into the array
      difference=( $rel_max_difference )
      echo "Difference between numerical fields in $file1 and $file2 -  Average: ${difference[0]}. Maximum: ${difference[1]}"
      diff -yr --suppress-common-lines $folder1 $folder2
      ret=1
    fi
  done
fi

# Files that are present only in reference or obtained
# folder
if [ -n "$only_files" ]; then
  echo "$only_files"
  ret=1
fi

exit $ret

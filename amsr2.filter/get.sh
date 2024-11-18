
tag=20230101

open="' 1 1 1 1 1'"
iced="' 3 3 3 3 3'"

#echo grep $open matched_$tag.txt 
#exit

grep ' 1 1 1 1 1' matched_$tag.txt > open_$tag.txt
grep ' 3 3 3 3 3' matched_$tag.txt > iced_$tag.txt
sort -nr -k 16 open_$tag.txt > a; mv a open_$tag.txt
sort -nr -k 16 iced_$tag.txt > a; mv a iced_$tag.txt


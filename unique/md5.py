import os
import sys

#Check sorted (by hash) listings of md5 hashes for duplicates
nmd5 = 0
fname = 1
oldmd5 = 0
oldline = "1 1 1 1 1 1 1 1 1 1 1 "
oldname = oldline.split()[fname]
k = 0

# use argument for fname
fin = open(sys.argv[1],"r")

# if path or name includes a space, 
#   a) skip
#   b) replace ( with \(, ) with \), ' with \'

for line in fin:
  words = line.split()

  md5 = words[nmd5] 
  name = words[fname].strip('()')
  #debug print("md5, name: ",md5, name, flush=True)

  if ( '\\' in name or '\ ' in name):
    #debug print("have a blank in ",name)
    continue
  
  if (md5 == oldmd5):
    k += 1
    #print("echo ",md5)
    print("cmp ",oldname, name)
    print("if [ $? -eq 0 ] ; then")
    print("  echo can rm one of ",oldname, name)
    print("fi\n")
  oldmd5 = md5
  oldline = line
  oldname = name

print("exit")
print(k, "possible matches")

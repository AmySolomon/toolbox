import os
import sys
import datetime

start = datetime.date(2024,2,1)
end = datetime.date(2024,2,29)
print(start, end)
dt = datetime.timedelta(1)

current = start
while (current <= end):
    dname = "giops."+current.strftime("%Y%m%d")
    if (os.path.exists(dname)):
        os.system("tar cf ../"+dname+".tar "+dname)
        #print("tar cf ../"+dname+".tar "+dname)
    else:
        print("no archive for ",current)

    current += dt

#!/usr/bin/python

# converts a gregorian date to julian date
# expects one or two arguments, first is date in dd.mm.yyyy,
# second optional is time in hh:mm:ss. If time is omitted,
# 12:00:00 is assumed

import math, sys, string
from datetime import *

#===============================================================================
# if len(sys.argv)==1:
#    print "\n gd2jd.py converts a gregorian date to julian date."
#    print "\n Usage: gd2jd.py dd.mm.yyyy [hh:mm:ss.ssss]\n"
#    sys.exit()
#===============================================================================
def convertDateTimeJul(date):
  
    dd=date.day
    mm=date.month
    yyyy=date.year
    

    hh= date.hour
    min = date.minute
    sec = date.second
   
    
    UT=hh+min/60+sec/3600
    
    #print "UT="+`UT`
    
    total_seconds=hh*3600+min*60+sec
    fracday=total_seconds/86400
    
    #print "Fractional day: %f" % fracday
    # print dd,mm,yyyy, hh,min,sec, UT
    
    if (100*yyyy+mm-190002.5)>0:
        sig=1
    else:
        sig=-1
    
    JD = 367*yyyy - int(7*(yyyy+int((mm+9)/12))/4) + int(275*mm/9) + dd + 1721013.5 + UT/24 - 0.5*sig +0.5
    
    months=["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
    
    #print "\n"+months[mm-1]+" %i, %i, %i:%i:%i UT = JD %f" % (dd, yyyy, hh, min, sec, JD),
    return int(JD + 0.5)

    
if __name__ == '__main__':
    print convertDateTimeJul(datetime(1980,3,2,12,0,0))
from ccu_gen_beta.models import *
from datetime import date
import pyUtilities as pyU
from BeautifulSoup import BeautifulSoup
from paths import *






def getADAStatsSenate2010():
    congressObj = Congress.objects.filter(beginDate__lte=date(2010,2,1),endDate__gte=date(2010,2,1))[0]
    #didn't want to build a whole new parser for the new pdf format so just coded by hand...
    dSenate2010 = {'Sessions AL':5,'Shelby AL':0,'Begich AK':85,'Murkowski AK':20,'KYL AZ':0,'MCCAIN AZ':0,'LINCOLN AR':70,'PRYOR AR':65,'BOXER CA':95,'FEINSTEIN CA':90,'BENNET CO':85,'UDALL CO':90,'DODD CT':85,'LIEBERMAN CT':75,'CARPER DE':90,'KAUFMAN DE':55,'LEMIEUX FL':5,'NELSON FL':90,'CHAMBLISS GA':0,'ISAKSON GA':5,'AKAKA HI':85,'INOUYE HI':80,'CRAPO ID':0,'RISCH ID':0,'BURRIS IL':60,'DURBIN IL':95,'BAYH IN':75,'LUGAR IN':25,'GRASSLEY IA':10,'HARKIN IA':100,'BROWNBACK KS':0,'ROBERTS KS':0,'BUNNING KY':0,'MCCONNELL KY':0,'LANDRIEU LA':75,'VITTER LA':5,'COLLINS ME':40,'SNOWE ME':40,'CARDIN MD':90,'MIKULSKI MD':90,'BROWN MA':20,'KERRY MA':85,'LEVIN MI':95,'STABENOW MI':90,'FRANKEN MN':90,'KLOBUCHAR MN':90,'COCHRAN MS':5,'WICKER MS':0,'BOND MO':0,'MCCASKILL MO':90,'TESTER MT':85,'BAUCUS MT':85,'JOHANNS NE':10,'NELSON NE':50,'ENSIGN NV':5,'REID NV':75,'GREGG NH':15,'SHAHEEN NH':90,'GREGG NH':90,'LAUTENBERG NJ':95,'MENENDEZ NJ':90,'BINGAMAN NM':90,'UDALL NM':95,'GILLIBRAND NY':100,'SCHUMER NY':95,'BURR NC':5,'HAGAN NC':85,'CONRAD ND':85,'DORGAN ND':95,'SHERROD OH':95,'VOINOVICH OH':80,'COBURN OK':5,'INHOFE OK':0,'MERKLEY OR':100,'WYDEN OR':100,'CASEY PA':90,'SPECTER PA':90,'REED RI':90,'WHITEHOUSE RI':90,'DEMINT SC':5,'GRAHAM SC':5,'JOHNSON SD':85,'THUNE SD':0,'ALEXANDER TN':10,'CORKER TN':5,'CORNYN TX': 0,'HUTCHISON TX':0,'BENNETT UT':15,'HATCH UT':0,'LEAHY VT':100,'SANDERS VT':95,'WARNER VA':80,'WEBB VA':85,'CANTWELL WA':90,'MURRAY WA':95,'ROCKEFELLER WV':85,'FEINGOLD WI':95,'KOHL WI':90,'BARRASSO WY':0,'ENZI WY':5}
    for name,score in dSenate2010.items():
        lastName = name.split()[0]
        abbrev = name.split()[1]
        try:
            rep = Rep.objects.get(lastName__iexact=lastName,state__abbrev=abbrev,senator=True,congress=congressObj)
        except Exception,ex:
            print ex
            print 'WHY NO REP FOR %s %s' % (lastName,abbrev)
            continue
        
        RepADA.objects.get_or_create(rep=rep,year=2010,adaScore=score)


def getADAStatsSenate2009(fileName):
     
       import string
       dateADA = date(2009,2,1) #sessions begin in january so jump bump up date a bit
       congressObj = Congress.objects.filter(beginDate__lte=dateADA,endDate__gte=dateADA)
       text = open(fileName,'r').read()
       text = text[text.lower().find('united states senate'):]
       text = text[text.lower().find('alabama')+8:text.lower().find('how liberal')]
       lsText = text.split('\n')
       lsText = [pyU.removePunctuation(line,lsExcept=['-','+']) for line in lsText if pyU.removePunctuation(line) != ""]
        
       stateName = 'ALABAMA'
       for text in lsText:
           line = text.split()

           #print line
           if len(line) == 0 or len(line) > 25:
               print 'HERE TOO SHORT OR LONG'
               continue
           elif line[0][1] in string.uppercase:
               if len(line) > 1 and line[1][1] in string.uppercase and line[1] != 'AL':
                   stateName = line[0] + ' ' + line[1]
               else:
                   stateName = line[0]
               #continue
           else: 
               lastName = line[0]
               adaAnswers = line[2:-1]

           if line[-1][0] in string.uppercase or line[-1][0] in '+-':
               print 'HERE'
               continue

           try:    
               adaScore = int(line[-1])
           except Exception,ex:
               print "PROBLEM WITH SCORE"
               print adaScore
               print ex
               continue

           print lastName
           print stateName
           print ""
           try:
               rep = Rep.objects.filter(lastName=lastName,state__name__iexact=stateName,congress=congressObj)[0]
           except Exception,ex:
               print "WHY NO REP %s %s " % (lastName,stateName)
               continue
           
           RepADA.objects.get_or_create(rep=rep,year=2009,adaScore=adaScore)
            

def getPartyPercentage(session,senate=True): 
    if senate:
        url = 'http://projects.washingtonpost.com/congress/%d/senate/members/' % session
    else:
        url = 'http://projects.washingtonpost.com/congress/%d/house/members/' % session
        
    html = pyU._getFile(url)
    doc = BeautifulSoup(html)    
    congressObj = Congress.objects.get(number=session)
    table = doc.find('table',{'class':'member-table'})
    rows = table.findAll('tr')
    for row in rows[1:]:
        lastName = row.find('a').string.split()[1]
        abbrev = row.findAll('td')[3].string
        score = int(row.findAll('td')[-1].string.replace('%',''))
        if score < 10:
            print 'ERROR WITH SCORE'
            score=-1
        print lastName
        print abbrev
        print score
        print ""
        try:
            if senate:
                rep = Rep.objects.get(congress=congressObj,lastName=lastName,state__abbrev=abbrev,senator=True)
            else:
                rep = Rep.objects.get(congress=congressObj,lastName=lastName,district__state__abbrev=abbrev,senator=False)
        except:
            print "WHY NO REP %s %s" % (lastName,abbrev)
            continue
         
        try:    
            RepWithParty.objects.get_or_create(rep=rep,congress=congressObj,withPartyScore=score)   
        except Exception,ex:
            print ex
            print rep


   
if __name__ == '__main__':
    # RepWithParty.objects.all().delete()
    getPartyPercentage(112,senate=False)        
    #     getPartyPercentage(112,senate=True) 
    #     getPartyPercentage(111,senate=False)        
    #     getPartyPercentage(111,senate=True)
    #RepADA.objects.all().delete()
    #getADAStatsSenate2009(CCU_DATA_PATH + 'ada_2009.txt')
    #getADAStatsSenate2010()
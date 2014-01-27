from ccu_gen_beta.models import *
from datetime import date
import pyUtilities as pyU
from BeautifulSoup import BeautifulSoup
import re
from ccu_utilities import createDate2
import string

def createElectionDates():
    
    Election.objects.get_or_create(date=date(2008,11,4),senateClass=2)
    Election.objects.get_or_create(date=date(2010,11,2),senateClass=3)
    Election.objects.get_or_create(date=date(2012,11,6),senateClass=1)

def getElectionPredsSenate(url):

    html = pyU._getFile(url)
    doc = BeautifulSoup(html)
    try:
        reportDate = createDate2(doc.find('h2',{'class':'date'}).string)
    except Exception:
        return #at this point passed in a faulty url
        
    congressObj = Congress.objects.get(beginDate__lt=reportDate,endDate__gt=reportDate)
    electionObj = Election.objects.filter(date__gt=reportDate).order_by('date')[0]
  
    tables = doc.findAll('table',{'id':re.compile('rr.*')})
    for table in tables:
        row = table.findAll('tr')[1]
        cols = table.findAll('td')
        for col in cols:
            paras = col.findAll('p')
            desig = None
            for index,para in enumerate(paras):
                if index == 0: desig = para.find('strong').string.split('(')[0].lower()
                else:
                    nameAbbrev = para.findAll(text=True)[0].split()  
                    retired = False
                    if nameAbbrev[0][1] in string.uppercase: 
                        stateAbbrev = nameAbbrev[0]
                        lastName = nameAbbrev[1]
                        retired = True
                    else:
                        stateAbbrev = nameAbbrev[1]
                        lastName = nameAbbrev[0]
                        
                    stateAbbrev = pyU.toascii(pyU.removePunctuation(stateAbbrev).strip()).split()[0]
                    lastName = pyU.toascii(pyU.removePunctuation(lastName).strip())
                    print stateAbbrev
                    print lastName
                    try: rep = Rep.objects.get(state__abbrev=stateAbbrev,lastName__iexact=lastName,congress=congressObj)
                    except Exception,ex: 
                        print congressObj
                        print lastName
                        print stateAbbrev
                        print ex
                        print ""
                        
                    
                    desigNew=None
                    if retired: desigNew = 'RETIRE'
                    elif desig.find('solid d') > -1: desigNew='SOLID_D'
                    elif desig.find('solid r') > -1: desigNew = 'SOLID_R'
                    elif desig.find('likely d') > -1: desigNew = 'LIKE_D'
                    elif desig.find('likely r') > -1: desigNew='LIKE_R'
                    elif desig.find('lean d') > -1: desigNew='LEAN_D'
                    elif desig.find('lean r') > -1: desigNew='LEAN_R'
                    elif desig.find('toss') > -1: desigNew='TU'
                    
                    predElectionObj = PredElection(election=electionObj,rep=rep,date=reportDate,pred=desigNew)
                    print predElectionObj
                    print ""
                    try:
                        predElectionObj.save()
                    except Exception,ex:
                        print ex
                        pass


def getAllElectionPreds(url,senate=True,summary=False):
    html = pyU._getFile(url) 
    doc = BeautifulSoup(html)
    urls = doc.find('div',{'class':'content-holder'}).findAll('a')
    for url in urls:
        url = 'http://www.cookpolitical.com' + url['href']
        print 'GETTING PRED FOR %s' % url
        if senate: getElectionPredsSenate(url)
        else: 
            if not summary:
                getElectionPredsHouse(url)
            else:
                getElectionSummaryHouse(url)
                
def getOldElectionPredsSenate(url):
    getAllElectionPreds(url)

def getMostCurrElectionPredsSenate():    
    url = 'http://www.cookpolitical.com'
    html = pyU._getFile(url) 
    doc = BeautifulSoup(html)
    url = url +  doc.find('a',{'title':re.compile('.*Race ratings')})['href']
    getAllElectionPreds(url)

def getElectionPredsHouse(url):

   doc = BeautifulSoup(pyU._getFile(url))
   try:
       reportDate = createDate2(doc.find('h2',{'class':'date'}).string)
   except Exception: #for weird urls
        return
        
   congressObj = Congress.objects.get(beginDate__lt=reportDate,endDate__gt=reportDate)
   electionObj = Election.objects.filter(date__gt=reportDate).order_by('date')[0]
   print congressObj

   for i in range(0,2):

      table1 = doc.findAll('table',{'width':'645'})[i]
      if i == 0:lsCols = ['likely d','lean d','tossup']
      else: lsCols = ['tossup','lean r','likely r'] 
      row = table1.findAll('tr')[1]
      cols = row.findAll('td',{'valign':'top'})

      for desig,col in zip(lsCols,cols):
          innerTable = col.find('table')
          innerRows = innerTable.findAll('tr')[1:]

          for ir in innerRows:
              retired=False
              ic = ir.findAll('td')
              
              stateAbbrev = ic[0].findAll(text=True)[0].split('-')[0]
              districtNum = ic[0].findAll(text=True)[0].split('-')[1]
              if districtNum.find('AL') > -1: districtNum = 0
              else: districtNum = int(districtNum)

              lastName = pyU.toascii(ic[1].findAll(text=True)[0])
              if lastName.lower().find('vacant') > -1: continue
              if lastName.lower().find('open') > -1: retired=True
              else: desig2 = desig
              lastName = pyU.removePunctuation(lastName).split()
              if len(lastName) > 1 and lastName[-1].lower().find('jr') == -1: lastName = lastName[-1]
              else: lastName = lastName[1]

              print lastName
              print stateAbbrev
              stateObj = State.objects.get(abbrev=stateAbbrev)

              try: 
                  rep = Rep.objects.get(district__state=stateObj,district__districtNum=districtNum,lastName__iequals=lastName,congress=congressObj)
              except Exception,ex: 
                  try:
                      rep = Rep.objects.get(district__state=stateObj,district__districtNum=districtNum,lastName__istartswith=lastName,congress=congressObj)
                  except Exception,ex:
                      print ex
                      continue

              print ""        
              if retired: desigNew = 'RETIRE'
              elif desig.find('solid d') > -1: desigNew='SOLID_D'
              elif desig.find('solid r') > -1: desigNew = 'SOLID_R'
              elif desig.find('likely d') > -1: desigNew = 'LIKE_D'
              elif desig.find('likely r') > -1: desigNew='LIKE_R'
              elif desig.find('lean d') > -1: desigNew='LEAN_D'
              elif desig.find('lean r') > -1: desigNew='LEAN_R'
              elif desig.find('toss') > -1: desigNew='TU'

              predElectionObj = PredElection(election=electionObj,rep=rep,date=reportDate,pred=desigNew)
              print predElectionObj
              print ""
              try:
                  predElectionObj.save()
              except Exception,ex:
                  print ex
                  pass


#getElectionPredsHouse('http://www.cookpolitical.com/charts/house/competitive_2010-06-24_12-45-01.php')   
#assert 0

def getElectionSummaryHouse(url):

   doc = BeautifulSoup(pyU._getFile(url))
   try:
       reportDate = createDate2(doc.find('h2',{'class':'date'}).string)
   except Exception: #for weird urls
        return
   
   congressObj = Congress.objects.get(beginDate__lt=reportDate,endDate__gt=reportDate)
   electionObj = Election.objects.filter(date__gt=reportDate).order_by('date')[0]

   table = doc.findAll('table')[1]
   rows = table.findAll('tr')
   for row in rows[3:]:
       try:
           ic = row.findAll('td')
           stateAbbrev = ic[0].string.split('-')[0]
           districtNum = ic[0].string.split('-')[1]
           if districtNum.find('AL') > -1: districtNum = 0
           else: districtNum = int(districtNum)

           lastName = pyU.toascii(ic[1].string)
           lastName = pyU.removePunctuation(lastName).split()
           if len(lastName) > 1 and lastName[-1].lower().find('jr') == -1: lastName = lastName[-1]
           else: lastName = lastName[1]
           status = ic[2].string.lower()

           print lastName
           print stateAbbrev
           print status
           print ""

           desig = None
           if status == 'retiring':
               desig = 'RETIRE'
           elif status.find('running') > -1:
               if status.find('senate') > -1: desig = 'RS'
               elif status.find('governor') > -1: desig = 'RG'
               elif status.find('mayor') > -1: desig = 'RM'
           elif status.find('potential') > -1:
               if status.find('retir') > -1: desig = 'PR'
               elif status.find('mayor') > -1: desig = 'PM'
               elif status.find('gov') > -1:desig = 'PG'
               elif status.find('sen') > -1: desig = 'PS'

           if desig==None:
               print status
               assert 0
               
           try: rep = Rep.objects.filter(district__state__abbrev=stateAbbrev,district__districtNum=districtNum,lastName__iendswith=lastName)[0]
           except Exception,ex: Rep.objects.filter(district__state__abbrev=stateAbbrev,district__districtNum=districtNum,lastName__istartswith=lastName)[0]
           predElectionObj = PredElection.objects.get_or_create(election=electionObj,rep=rep,date=reportDate,pred=desig)[0]
           print predElectionObj
           print ""
           predElectionObj.save()   

       except Exception,ex:
           print ex
           continue

def getMostCurrElectionPredsHouse():    
   url = 'http://www.cookpolitical.com/node/4056/'
   getAllElectionPreds(url,senate=False)
   url = 'http://www.cookpolitical.com/node/4058' #house summary
   getAllElectionPreds(url,senate=False,summary=True)
   
def getOldElectionPredsHouse(urlGeneral,urlSummary):
       getAllElectionPreds(urlGeneral,senate=False)
       getAllElectionPreds(urlSummary,senate=False,summary=True)
    
if __name__ == '__main__':
    getMostCurrElectionPredsSenate()
    assert 0
    #getOldElectionPredsHouse('http://www.cookpolitical.com/node/10439','http://www.cookpolitical.com/node/10446') #for 2010
    #assert 0
    getMostCurrElectionPredsSenate()
    #for 2010 race
    getOldElectionPredsSenate('http://www.cookpolitical.com/node/10438')
    #for 2008 race
    getOldElectionPreds('http://www.cookpolitical.com/node/9939')
   
from ccu_gen_beta.models import *
from ccu_utilities import createDate2
import pyUtilities as pyU
from BeautifulSoup import BeautifulSoup
import re

#get latest state populations from wikipedia
def getStatePops():
    html = pyU._getFile('http://en.wikipedia.org/wiki/List_of_U.S._states_and_territories_by_population',cachedFile=False)
    doc = BeautifulSoup(html)
    table = doc.find('table',{'class':re.compile('wikitable*')})
    rows = table.findAll('tr')
    #get latest population date
    censusDateNew = createDate2(pyU.stripWords(rows[0].findAll('th')[3].findAll(text=True)[1]))
    censusDateOld = createDate2(pyU.stripWords(rows[0].findAll('th')[5].findAll(text=True)[1]))
    print censusDateNew
    print censusDateOld

    
    for row in rows[1:57]:
        cols = row.findAll('td')
        stateName = cols[2].find('a').string.replace('.','')
        popNew = int(cols[3].string.replace(',',''))
        popOld = int(cols[5].string.replace(',',''))
        print stateName
        if stateName.find('DC') > -1:
            stateObj = State.objects.get(name__icontains='district')
        elif stateName.find('Virgin Is') > -1:
            stateObj = State.objects.get(name__icontains='virgin is')
        elif stateName.find('Mariana Is') > -1:
            stateObj = State.objects.get(name__icontains='mariana is')
        elif stateName.find('Samoa') > -1:
            stateObj = State.objects.get(name__icontains='samoa')
        else:
            try:
                stateObj = State.objects.get(name=stateName.upper())
            except:
                stateObj = State.objects.get(name__icontains=stateName.upper())
        
        try:
            statePopObj = StatePop.objects.get_or_create(state=stateObj,pop=popNew,date=censusDateNew)
        except Exception,ex:
            pass
        
        try:
            statePopObj = StatePop.objects.get_or_create(state=stateObj,pop=popOld,date=censusDateOld)
        except Exception,ex:
            pass

def getStatePVI(year):
    html = pyU._getFile('http://en.wikipedia.org/wiki/Cook_Partisan_Voting_Index',cachedFile=False)
    doc = BeautifulSoup(html)
    stateTags = doc.findAll('td',{'width':'50%'})[1].find('table').findAll('tr')

    for tag in stateTags[1:]:
        
        cook_pvi_tag  = tag.contents[3].contents[1]
        name = pyU.toascii(tag.contents[1].contents[0].string.lower())
        try:
            stateObj = State.objects.get(name__iexact=name)
        except:
            print "WHY NO STATE OBJ FOR %s ---------------------" % name
            continue
        
        if cook_pvi_tag.find('+') > -1:
                rep_or_d_cook = cook_pvi_tag.split('+')[0].replace('+','')
                margin = int(cook_pvi_tag.split('+')[1].strip())

                if rep_or_d_cook == 'R':
                    demCook = False
                else:
                    demCook = True
                scoreCook = margin
        
        elif cook_pvi_tag.find('EVEN') > -1 and stateObj:
                demCook = False
                scoreCook = 0
       
        pviObj = StatePVI.objects.get_or_create(year=year,state=stateObj,scoreCook=scoreCook,demCook=demCook)
        print pviObj

def getDistrictPVI(year):
    html = pyU._getFile('http://en.wikipedia.org/wiki/Cook_Partisan_Voting_Index',cachedFile=False)
    doc = BeautifulSoup(html)
    tags = doc.findAll('td',{'width':'50%'})[0].find('table').findAll('tr')

    for tag in tags[1:]:
        cook_pvi_tag  = tag.contents[-4].contents[1]
        name = pyU.toascii(tag.contents[1].contents[0].string.lower())
        try:
            stateObj = State.objects.get(name__iexact=name)
        except:
            print "WHY NO STATE OBJ FOR %s ---------------------" % name
            continue
        
        if tag.contents[3].contents[0].string.lower().find('at') == -1:
            districtNum = int(pyU.stripCardinalNum(tag.contents[3].contents[0].string))
        else:
            districtNum = 0    
        
        try: 
            districtObj = District.objects.get(state=stateObj,districtNum=districtNum)
        except: 
            print "WHY NO DISTRICT OBJ FOR %s %d-------------------" % (str(stateObj),districtNum)    


        if cook_pvi_tag.find('+') > -1:
                rep_or_d_cook = cook_pvi_tag.split('+')[0].replace('+','')
                margin = int(cook_pvi_tag.split('+')[1].strip())

                if rep_or_d_cook == 'R':
                    demCook = False
                else:
                    demCook = True
                scoreCook = margin

        elif cook_pvi_tag.find('EVEN') > -1 and stateObj:
                demCook = False
                scoreCook = 0

        pviObj = DistrictPVI.objects.get_or_create(year=year,scoreCook=scoreCook,demCook=demCook,district=districtObj)
        print pviObj

if __name__ == '__main__':
    
    getStatePVI(2010)
    #getDistrictPVI(2010)
    #pass
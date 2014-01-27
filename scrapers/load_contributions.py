from ccu_gen_beta.models import *
import pyUtilities as pyU
from BeautifulSoup import BeautifulSoup
import re
import csv
from ccu_utilities import createDate3,findJonesSubTopicPres
import datetime
from paths import *

#later, use this CRP_Categories file to create a hierarchy for sector, industry, business
def updateID():
    f = open(CCU_DATA_PATH + 'CRP_Categories.txt')
    all_text = f.read()
    all_text = all_text.split('Sector Long')[1]
    lines = all_text.split('\n')[1:-1]
    for line in lines:
        cats = line.split('\t')

        try:
            ml = MapLightBusiness.objects.get(name=cats[1].replace("'",'').strip())
            ml.mlID = cats[0]
            ml.save()
            print 'BUSINESS FOUND %s' % str(ml)
        except Exception:
            #print cats[1]
            ml = MapLightBusiness.objects.filter(name__istartswith=cats[1].strip(),mlID=None)
            if len(ml) > 0:
                #print 'FOUND'
                #print ml[0]
                ml[0].mlID = cats[0]
                ml[0].save()
            else:
                print "SECTOR_INDUSTRY_OR_BUSINESS NOT FOUND"
                sectorName = cats[-2]
                industryName = cats[3]
                busName = cats[1]
                busCode = cats[0]
                print sectorName
                print MapLightSector.objects.filter(name__istartswith=sectorName)
                print industryName
                print MapLightIndustry.objects.filter(name__istartswith=industryName)
                print busName
                print busCode

                print ""
    print "-----------------------------------"
    for bus in MapLightBusiness.objects.all():
        if not bus.mlID:
            print 'NO ID FOR %s' % bus

def loadMapLightInterestGroups():
    html = pyU._getFile('http://maplight.org/us-congress/interest',cachedFile=False)
    doc = BeautifulSoup(html)
    
    groupLinks = doc.findAll('a',{'class':re.compile('.*-link.*')})
    sector=None
    industry=None
    for link in groupLinks:
        name = pyU.stripWords(link.string.replace('&amp;','&'))
        print name
        print link
        if link['class'].find('sector') > -1:
            print 'sector'
            sector = MapLightSector.objects.get_or_create(name=name)[0]
        elif link['class'].find('industry') > -1:
            industry = MapLightIndustry.objects.get_or_create(sector=sector,name=name)[0]
            print 'industry'
        elif link['class'].find('business') > -1:
            bus = MapLightBusiness.objects.get_or_create(industry=industry,name=name)[0]
            print 'business'
        print ''
    updateID()



def loadIGContributions(fileName,year):
    
    found = False
    print fileName
    
    lastObj = RepContribution.objects.latest('pubDate')
   
    fDictReader = csv.DictReader(open(fileName,'rb'))
    
    numRows = 0
    for row in fDictReader:
        # if (createDate3(row['date'])) != date(2010,5,12):
        #             continue
            
        numRows+=1
        
        if row['transaction_id'].strip() == '':
            continue
        
        
        print row['transaction_id']
        if not found:
            if lastObj.rbID == row['transaction_id']:
                found=True
                print numRows
              
        if not found:
            continue
        
        #this is a weird business that hasn't been coded for...
        if MapLightBusiness.objects.filter(mlID=row['contributor_category']).count() == 0:
            continue
       
        #because this is a lot of contribution data, only store data for reps/senators in database
        #this means for any new senator/rep will have to rerun this function...
        if Rep.objects.filter(repID=row['recipient_ext_id']).count() > 0:
            
            rc = RepContribution()
            rc.rbID = row['transaction_id']
            rc.rep = Rep.objects.filter(repID=row['recipient_ext_id'])[0]
            rc.amountContr = float(row['amount'])
            rc.dateContr = createDate3(row['date'])
            rc.contribName = row['contributor_name']
            rc.contribID = row['contributor_ext_id']
            
            try:
                rc.mlBusiness = MapLightBusiness.objects.get(mlID=row['contributor_category'])
            except Exception,ex:
                print ex
                print row['contributor_category']
                continue
            #print mlBusiness.industry.sector

            if row['transaction_id'].lower().find('indiv') > -1:
                rc.contribOCC = row['contributor_occupation']
                rc.contribEmployer = row['contributor_employer']
                try:
                    rc.contribState = State.objects.get(abbrev=row['contributor_state'])
                except Exception,ex:
                    print ex
                    continue
                rc.contribZipCode = row['contributor_zipcode']
                rc.isPAC = False
            else:
                rc.isPAC=True
            #print 'SAVED'
            rc.pubDate = datetime.datetime.now()
            # try:
            #                 if rc.rep.lastName=='Lincoln':
            #                     print rc
            #                     print row
            #                     print ""
            #             except Exception:
            #                 pass
            #print 'adding row'
            rc.save()
             
# def mapMLBusinessToSubtopics():
#     
#     allTopics = [topic for topic in JonesTopic.objects.all()]
#     sameAsLast=False
#     for i,bus in enumerate(MapLightBusiness.objects.all()):
#         print i
#         if i == 1:
#             sameAsLast=True
#         
#         subtopicsD = findJonesSubTopicPres(bus.name,allTopics,score=0.3,sameAsLast=sameAsLast)
#         print subtopicsD
#         bus.subtopics = []
#         bus.save()
#         [bus.subtopics.add(st) for st in subtopicsD.keys()]
#         print bus.subtopics.all()
#         bus.save()


if __name__ == '__main__':
    #mapMLBusinessToSubtopics()
    #pass
    
    #3249833
    #loadIGContributions(CCU_DATA_PATH + 'campaign contributions/contributions.fec.2002.csv',2002)  
    #loadIGContributions(CCU_DATA_PATH + 'campaign contributions/contributions.fec.2004.csv',2004)
    #loadIGContributions(CCU_DATA_PATH + 'campaign contributions/contributions.fec.2006.csv',2006)
    #loadIGContributions(CCU_DATA_PATH + 'campaign contributions/contributions.fec.2008.csv',2008)
    loadIGContributions(CCU_DATA_PATH + 'campaign contributions/contributions.fec.2010.csv',2010)
   
    
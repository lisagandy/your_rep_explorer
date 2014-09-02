from BeautifulSoup import BeautifulSoup
from your_rep_explorer.ccu_gen_beta.models import *
from ccu_utilities import createDate3
import pyUtilities as pyU
from urllib import urlretrieve
import datetime

def loadRepAnomalies():
    rep = Rep.objects.get_or_create(firstName='Kirsten',lastName='Gillibrand',senator=True,congress=Congress.objects.get(number=111),swornInDate=date(2009,1,26),endDate=date(2012,12,31))[0]
    rep.repID='N00027658'
    rep.repGovTrackID = '41223'
    rep.state = State.objects.get(name='NEW YORK')
    rep.save()

def loadReps(url):
   
    start = datetime.datetime.now()
    xml = pyU._getFile(url,cachedFile=False)
    doc = BeautifulSoup(xml)
    congressNum = int(doc.find('people')['session'])
    congressObj = Congress.objects.get(number=congressNum)
    
    reps = doc.findAll('person')
    end = datetime.datetime.now()
    print end-start
    
    
    for person in reps:
        start = datetime.datetime.now()    
        isThere = False
        try:
            repObj,isThere = Rep.objects.get_or_create(congress=congressObj,repID=person['osid'])
        except Exception,ex:
            print ex
            repObj = Rep()
        
        if isThere:
            print 'REP ALREADY THERE'
            continue
            
        repObj.repGovTrackID = person['id']
        repObj.congress = congressObj
        repObj.repID = person['osid']
        repObj.firstName = person['firstname']
        try: repObj.nickName = person['nickname'] 
        except Exception: pass
        try: repObj.middlename = person['middlename'] 
        except Exception: pass
        repObj.lastName = person['lastname']
        
        #change this for date in a sec
        try: repObj.birthday = createDate3(person['birthday']) 
        except Exception: pass
        try: repObj.gender = person['gender'] 
        except Exception: pass
        try: repObj.youtubeID = person['youtubeid'] 
        except Exception: pass
        try: repObj.religion = person['religion'] 
        except Exception: pass
        try: repObj.twitterID = person['twitterid'] 
        except Exception: pass
        
        role = person.find('role')
        stateObj = State.objects.get(abbrev=role['state'])
        
        if role['type']=="rep": 
            repObj.senator=False
            districtObj = District.objects.get(districtNum=int(role['district']),state=stateObj)
            repObj.district=districtObj
        else: 
            repObj.senator=True
            repObj.state = stateObj
            #print role['class']
            repObj.senatorClass = int(role['class'])
        
        repObj.swornInDate = createDate3(role['startdate'])
        if not repObj.swornInDate:
            repObj.swornInDate = date(1600,1,1)
            
        repObj.endDate = createDate3(role['enddate'])
    
        if role['party']=="Democrat": repObj.party='D'
        elif role['party']=="Republican": repObj.party='R'
        else: role['party']='I'
        
        try: repObj.website=role['url'] 
        except Exception: pass
        try: repObj.address=role['address'] 
        except Exception: pass
        repObj.save()
        try:
            print repObj
        except Exception:
            continue
        end = datetime.datetime.now()
        delta = end-start
        print delta.seconds
        print delta.microseconds
        #assert 0
        
def downloadPics(url):
    downloadPath = '/Users/lisagandy/infolab_projects/ccu_beta/media/static/images/senators/'
    
    for rep in Rep.objects.filter(senator=True):
        try:
            print rep
        except Exception:
            pass
        fileIn = 'http://www.govtrack.us/data/photos/%s.jpeg' % rep.repGovTrackID
        fileOut = downloadPath + ('/%s.jpeg' % rep.repGovTrackID)
        urlretrieve(fileIn,fileOut)
      
if __name__ == '__main__':
    #loadRepAnomalies()
    #assert 0
    #Rep.objects.all().delete()
    #loadReps('http://www.govtrack.us/data/us/111/people.xml')
    loadReps('http://www.govtrack.us/data/us/112/people.xml')
    #downloadPics('http://www.govtrack.us/data/photos/')
    
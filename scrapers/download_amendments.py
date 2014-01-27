import dircache
from BeautifulSoup import BeautifulSoup
from ccu_utilities import createDate3
from ccu_gen_beta.models import *
import pyUtilities as pyU
import xml
from paths import *
import datetime   

def downloadAmendments(sessionNum):
    
    
    for fileName in dircache.listdir(CCU_DATA_PATH + '%d_amendments/' % sessionNum):
        start = datetime.datetime.now()
        print fileName
        #if fileName.find('h822') == -1:
            #continue
        if fileName.find('txt') > -1:
            continue
            
        doc = BeautifulSoup(open(CCU_DATA_PATH + '%d_amendments/%s' % (sessionNum,fileName)).read())
        chamber = doc.find('amendment')['chamber']

        number = doc.find('amendment')['number']
        #print doc.find('amends')['type']
        #print doc.find('amends')['number']
        try:
            bill = Bill.objects.get(congress__number=sessionNum,prefix=doc.find('amends')['type'],number=int(doc.find('amends')['number']))
            #print bill 
        except Exception,ex:
            print ex 
            #print senate
            print doc.find('amends')['type']
            print doc.find('amends')['number']
            print int(doc.find('amends')['number'])
            assert 0
            #continue #amends a house bill...
          
        if Amendment.objects.filter(number=chamber+number,bill=bill).count() > 0:
            continue
              
        amendObj = Amendment.objects.get_or_create(number=chamber+number,bill=bill)[0]
        
        status = doc.find('status').string
        statusDate  = createDate3(doc.find('status')['datetime'].split('T')[0])
        statusObj = AmendStatus.objects.get_or_create(status=status,statusDate=statusDate)[0]
        amendObj.status.add(statusObj)
        
        try:
            sponsor = Rep.objects.get(repGovTrackID=doc.find('sponsor')['id'],congress__number=sessionNum)
            amendObj.sponsor=sponsor
        except Exception,ex:
            print ex
            sponsorComm = doc.find('sponsor')['committee']
            commObj = Committee.objects.filter(congress__number=sessionNum,name__istartswith=sponsorComm.split()[0],name__iendswith=sponsorComm.split()[-1])[0]
            amendObj.sponsorComm = commObj
            
        offeredDate = doc.find('offered')['datetime']
        amendObj.offeredDate = offeredDate
        
        description = doc.find('description').string
        amendObj.description=description
        
        purpose = doc.find('purpose').string
        amendObj.purpose=purpose
        
        sequence = doc.find('amends')['sequence']
        if sequence != "":
            amendObj.sequence=int(sequence)
       
        text = None
        try:
            print fileName
            textFile =  CCU_DATA_PATH + '%d_amendments/%s.txt' % (sessionNum,fileName.split('.xml')[0])
            print textFile
            f = open(textFile)
            text = f.read()
            text = pyU.toascii(text)
            text =  xml.sax.saxutils.unescape(text).replace('&quot;','"').replace('&#039;','')
        except Exception,ex:
            print "NOT A BIG DEAL"
            print ex
            
        amendObj.text = text
        #print text
        print 'Saved amendment'
        amendObj.save()
        end = datetime.datetime.now()
        delta = end-start
        print delta.seconds
        print delta.microseconds
        assert 0

if __name__ == '__main__':
    #downloadAmendments(111)
    downloadAmendments(112)
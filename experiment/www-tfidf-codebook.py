import dircache
from ccu_utilities import *
from ccu_gen_beta.models import JonesSubTopic,Vote
from BeautifulSoup import BeautifulSoup
from paths import *
from prediction3 import classify

lsTopics = JonesTopic.objects.all()

def downloadSenateVotes(sessionNum):
    for fileName in dircache.listdir(CCU_DATA_PATH + '%d_votes/' % sessionNum):
        if fileName.find('h') > -1: continue #only get senate votes...
       
        xml = open(CCU_DATA_PATH + '%d_votes/%s' % (sessionNum,fileName))
        doc = BeautifulSoup(xml)
        try:
            bill = Bill.objects.get(congress__number=sessionNum,prefix=doc.find('bill')['type'],number=int(doc.find('bill')['number']))  
        except Exception,ex:
            print "NOMINATION OR SOMETHING ELSE WITH NO BILL-----------"
            print ex
            continue
        
        
        rollNumber = int(doc.find('roll')['roll'])
        #print rollNumber
        vote = Vote()
        vote.active=True
        vote.number = rollNumber
        vote.bill = bill
        if Vote.objects.filter(number=rollNumber,bill=bill).count() > 0:
            continue
        
        dateVote = createDate3(doc.find('roll')['datetime'].split('T')[0])
        vote.dateVote = dateVote
        
        numAye = int(doc.find('roll')['aye'])
        numNay = int(doc.find('roll')['nay'])
        numNV = int(doc.find('roll')['nv'])
        numPresent = int(doc.find('roll')['present'])
        vote.numAye = numAye
        vote.numNay = numNay
        vote.numNV = numNV
        vote.numPresent = numPresent
        
        category = doc.find('category').string
        catObj = VoteCategory.objects.get_or_create(category=category)[0]
        vote.category = catObj
        
        voteType = doc.find('type').string
        typeObj = VoteType.objects.get_or_create(voteType=voteType)[0]
        vote.voteType = typeObj
        
        question = doc.find('question').string
        vote.question = question
        
        result = doc.find('result').string
        resultObj = VoteResult.objects.get_or_create(voteResult=result)[0]
        vote.result = resultObj
        
       
        strReq = doc.find('required').string
        percentReq = int(strReq.split('/')[0]) / float(strReq.split('/')[1])
        
        vote.percentNeeded = percentReq
        vote.percentGotten = numAye/float(numAye+numNay+numNV+numPresent)
        
        if doc.find('amendment'):
            amendmentNum = doc.find('amendment')['number']
            amendObj = Amendment.objects.get(number=amendmentNum,bill__congress__number=sessionNum)
            vote.hasAmendment=True
            vote.amendment=amendObj
        
        try:
            vote.save()
        except Exception:
            continue
        
        for voter in doc.findAll('voter'):
            rep = Rep.objects.get(repGovTrackID=voter['id'],congress__number=sessionNum)
            if voter['vote'] == '+': voteCast = 'AYE'
            elif voter['vote'] == '-': voteCast='NAY'
            elif voter['vote'] == '0':voteCast='NV'
            else: voteCast='PR'
            rv = RepVote.objects.get_or_create(rep=rep,voteCast=voteCast)[0]
            vote.repVotes.add(rv)
        
        vote.save()
        print vote
        print ""

def genericAmendText(text):
    text = text.lower()
    if text.find('nature') > -1:
        return True
    if text.find('not available') > -1:
        return True
    if text.find('instructions') > -1:
        return True
    if text.find('clarify standing') > -1:
        return True
    return False

def aboutBillOrRes(text):
    text = text.lower()
    if text.find('bill') > -1:
        return True
    if text.find('resolution') > -1:
        return True
    if text.find('cloture') > -1:
        return True
    return False

def findJonesSubTopicVote(text):
    global lsTopics    
    subtopicsD = findJonesSubTopicPres(text,lsTopics,score=0.14)
    cosineScore = []
    topics = []
    for topic,cs in subtopicsD.items():
        topics.append(topic)
        cosineScore.append(cs)
    
    lsTopic = zip(cosineScore,topics)
    lsTopic.sort()
    try:
        cosineScore,topics = zip(*lsTopic)
    except Exception:
        return None
        
    return topics[-1]
    
    
if __name__ == '__main__':
    downloadSenateVotes(112)
    
            
            
            
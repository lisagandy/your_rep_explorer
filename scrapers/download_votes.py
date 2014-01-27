import dircache
from ccu_utilities import *
from ccu_gen_beta.models import JonesSubTopic,Vote
from BeautifulSoup import BeautifulSoup
from paths import *
import datetime
#from prediction3 import classify


def downloadVotes(sessionNum):
    for i,fileName in enumerate(dircache.listdir(CCU_DATA_PATH + '%d_votes/' % sessionNum)):
        start = datetime.datetime.now()
        print i
        print fileName
        
        xml = open(CCU_DATA_PATH + '%d_votes/%s' % (sessionNum,fileName))
        doc = BeautifulSoup(xml)
        try:
            bill = Bill.objects.get(congress__number=sessionNum,prefix=doc.find('bill')['type'],number=int(doc.find('bill')['number']))  
        except Exception,ex:
            print "NOMINATION OR SOMETHING ELSE WITH NO BILL-----------"
            print ex
            continue
        
        rollNumber = int(doc.find('roll')['roll'])
        
       
        oldVote = Vote.objects.filter(number=rollNumber,bill=bill)
        print oldVote.count()
        if oldVote.count() > 0:
            #print 'VOTE ALREADY THERE'
            #print doc.find('roll')['where']
            vote = oldVote[0]
            if str(doc.find('roll')['where']).lower()=='house':
                vote.senateVote=False
            else:
                print "IN TRUE"
                vote.senateVote=True
            vote.save()
            #print vote.senateVote
            continue
        
        vote = Vote()
        print doc.find('roll')['where']
        
        if str(doc.find('roll')['where']).lower()=='house':
            vote.senateVote=False
        else:
            print "IN TRUE"
            vote.senateVote=True
        vote.active=True
        vote.number = rollNumber
        vote.bill = bill
        
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
        
        allCats= [vt.category for vt in VoteCategory.objects.all()]
        if category not in allCats:
            catObj = VoteCategory.objects.create(category=str(category))
            catObj.save()
            vote.category=catObj
        else:
            cat = VoteCategory.objects.filter(category=str(category))[0]
            vote.category=cat
        
        voteType = doc.find('type').string
        typeObj = VoteType.objects.get_or_create(voteType=str(voteType))[0]
        vote.voteType = typeObj
        
        question = doc.find('question').string
        vote.question = str(question)
       
        result = doc.find('result').string
        resultObj = VoteResult.objects.get_or_create(voteResult=str(result))[0]
        vote.result = resultObj
       
        strReq = str(doc.find('required').string)
        percentReq = int(strReq.split('/')[0]) / float(strReq.split('/')[1])
        
        vote.percentNeeded = percentReq
        vote.percentGotten = numAye/float(numAye+numNay+numNV+numPresent)
        
        
        
        if doc.find('amendment'):
            if doc.find('amendment')['ref'].find('serial') == -1:
                amendmentNum = doc.find('amendment')['number']
            else:
                tempNum = int(doc.find('amendment')['number'])
                amendmentNum = Amendment.objects.filter(bill=bill).order_by('number')[tempNum-1].number
                
            print amendmentNum
            print sessionNum
            amendObj = Amendment.objects.get(number=amendmentNum,bill__congress__number=sessionNum)
            vote.hasAmendment=True
            vote.amendment=amendObj
        
        try:
            print 'NEW VOTE '
            print vote
            print vote.senateVote
            vote.save()
        except Exception,ex:
            print ex
            assert 0
            continue
        
        for voter in doc.findAll('voter'):
            rep = Rep.objects.get(repGovTrackID=voter['id'],congress__number=sessionNum)
            if voter['vote'] == '+': voteCast = 'AYE'
            elif voter['vote'] == '-': voteCast='NAY'
            elif voter['vote'] == '0':voteCast='NV'
            else: voteCast='PR'
            rv = RepVote.objects.get_or_create(rep=rep,voteCast=voteCast)[0]
            vote.repVotes.add(rv)
        
        print 'NEW VOTE 2'
        vote.save()
        print vote
        print vote.senateVote
        end = datetime.datetime.now()
        delta = end - start
        print delta.seconds
        print delta.microseconds
        assert 0
       

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

# def findJonesSubTopicVote(vote):
#     
#         vote.subtopics=[]
#         vote.save()    
#         if vote.amendment:
#             #continue
#             #use text of amendment to find subtopics....
#             amendmentText = None
#             if not genericAmendText(vote.amendment.purpose):
#                 amendmentText = vote.amendment.purpose
#             else:
#                 return
#             
#             if not genericAmendText(vote.amendment.description) and amendmentText != vote.amendment.description:
#                 amendmentText = amendmentText + ' ' + vote.amendment.description
#             
#             if vote.amendment.text and not genericAmendText(vote.amendment.text):
#                 amendmentText = amendmentText + ' ' + vote.amendment.text
#             
#             if not amendmentText:
#                 return
#                 
#             amendmentText = amendmentText.split('as follows')[0]    
#             
#             #get all topics of bill to kind of narrow things down a bit....
#             subjects = vote.bill.subjects.all()
#             topics = []
#             for subject in subjects:
#                 for subtopic in subject.subtopics.all():
#                     if subtopic.topic not in topics:
#                         print subtopic
#                         topics.append(subtopic.topic)
#             
#             if topics == []: return
#             subtopicsD = findJonesSubTopicPres(amendmentText,topics,score=0.25)
#             return subtopicsD.keys()
#             
#         
#         elif vote.bill.summary.strip() != "": #if aboutBillOrRes(vote.voteType.voteType)s:
#                #print 'HERE'
#                vote.subtopics = []
#                #just assign all subtopics of the bill to the vote...
#                lsSubtopics = []
#                topics = []
#                for subject in vote.bill.subjects.all():
#                    #print 'SUBJECT %s' % subject
#                    for subtopic in subject.subtopics.all():
#                        #print '     SUBTOPIC %s w/ topic %s' % (subtopic.name,subtopic.topic.name)
#                        if subtopic not in lsSubtopics:
#                            lsSubtopics.append(subtopic)
#                        if subtopic.topic not in topics:
#                            topics.append(subtopic.topic)
#                #print vote.bill.summary
#                #print topics
#                subtopicsD = findJonesSubTopicPres(vote.bill.summary,topics,score=0.14)
#                return subtopicsD.keys()
#         else:
#             return []
#         #             lsSubtopics = []
#         #             for subject in vote.bill.subjects.all():
#         #                    print 'SUBJECT %s' % subject
#         #                    for subtopic in subject.subtopics.all():
#         #                        print '     SUBTOPIC %s w/ topic %s' % (subtopic.name,subtopic.topic.name)
#         #                        if subtopic not in lsSubtopics:
#         #                            lsSubtopics.append(subtopic)
#         #             
#         #             [vote.subtopics.add(st) for st in lsSubtopics]
#             
#             
#         #print vote.subtopics.all()
# 
# def cleanText(text):
#             import string
# 
#             words= ['strike','year','resolut','legis','table','bill','pass','amend','title','subtitle','specif','author','prohibit','juris','respons','submit','enhance','include','publish','requir','set']
#             words.extend(['add','continue','event','purpose','remov','establ','instruct','develop','designate','direct','provide','senate'])
#             words.extend(['congress','report','plan','exclude','confirm','forth','includ','consider','secretar','report','implemen'])
#             words.extend(['h.r.','section','sub','date','act','regard','earli','early','use','certain','west','east','north','south','clarify','propos','nation'])
#             words.extend(['introduc','approp','admin','process','affect','promote','program','prescribe','assist','reduce','facilit','communit','committee','project'])
#             words.extend(['revis','improv','increase','likel','carry','assoc','agree','control','develop','service','approv','program','participate','make','recommend','change','integra'])
#             #words.extend(['incr','limit','def','revis','alloc','program','leverag','provid','encourag','meet','federal','nation'])
#             words.extend(['primar'])
# 
#             text = text.lower()
#             text = text.split('as follows')[0]
#             reTitle1 = re.compile('mr.\s*\S*,',re.I)
#             reTitle2 = re.compile('ms.\s*\S*,',re.I)
#             reTitle3 = re.compile('mrs.\s*\S*,',re.I)
#             reParen = re.compile("\(.*?\)")
#             reNum = re.compile('\d+')
# 
#             text = re.sub(reTitle1,' ',text)
#             text = re.sub(reTitle2,' ',text)
#             text = re.sub(reTitle3,' ',text)
#             text = re.sub(reParen,'' ,text)
#             text = re.sub(reNum,'',text)
#             text = text.replace('mr.','').replace('ms.','').replace('mrs.','')
# 
#             for rep in Rep.objects.all():
#                 text = text.replace(rep.lastName.lower(),'')
# 
# 
#             for word in words:
#                 reWord = re.compile('\s+' + word + '\w*\s*')
#                 text = re.sub(reWord,' ',text)
# 
#             for stateName in stateAbbrevs.values():
#                 reWord = re.compile(stateName + '\w*\s*',re.I)
#                 text = re.sub(reWord,'',text)
# 
#             #print 'after statenames'
#             #print text
#             text = pyU.removePunctuation(text)
#             text = pyU.sStripStopWordsAll(text)    
#             #print 'after punc and strip words'
#             #print text
#             return text       
# 
# #ADD SOMETHING WHEN BILL OR AMENDMENT HAS ALREADY BEEN PROCESSED...
# def findJonesSubTopicVotesSVM(vote):
#                 print vote.amendment.subtopicsAssigned
#                 print ""
#                 print ""
#                 print "------------------------------------------"
#                 print vote
#                
#                 if vote.amendment and not vote.amendment.subtopicsAssigned:
#                     #return
#                     #use text of amendment to find subtopics....
#                     amendmentText = None
#                     if not genericAmendText(vote.amendment.purpose):
#                         amendmentText = vote.amendment.purpose
#                     else:
#                         print 'generic amendment'
#                         print vote.amendment.purpose
#                         return
# 
#                     if not genericAmendText(vote.amendment.description) and amendmentText != vote.amendment.description:
#                         amendmentText = amendmentText + ' ' + vote.amendment.description
# 
#                     if vote.amendment.text and not genericAmendText(vote.amendment.text):
#                         amendmentText = amendmentText + ' ' + vote.amendment.text
# 
#                     if not amendmentText:
#                         print 'no amendment text'
#                         return
# 
#                     print 'AMENDMENT'
#                     print amendmentText
#                     amendmentText = cleanText(amendmentText)
#                     print "---------------"
#                     print amendmentText
#                     subtopics = classify(amendmentText)
#                     print subtopics
#                     if len(subtopics) == 0:
#                         print 'using generic jones topic'
#                         subtopics = findJonesSubTopicVote(vote)
# 
#                     vote.amendment.subtopics = subtopics
#                     vote.amendment.subtopicsAssigned=True
#                     vote.amendment.save()
#                     print vote.amendment.subtopics.all()
# 
# 
#                 elif vote.bill.summary.strip() != "" and not vote.bill.subtopicsAssigned: #if aboutBillOrRes(vote.voteType.voteType)s:
#                       subjects = vote.bill.subjects.all()
#                       topics = []
#                       for subject in subjects:
#                           for subtopic in subject.subtopics.all():
#                               if subtopic.topic not in topics:
#                                   #print subtopic
#                                   topics.append(subtopic.topic)
# 
#                       print 'BILL'
# 
#                       summary = vote.bill.summary
#                       if len(summary) > 5000:
#                           summary = summary[0:5000]
#                       print summary
#                       print "----------------------"
#                       #print len(vote.bill.summary)
# 
#                       subtopics = []
#                       for sentence in pyU.lsSplitIntoSentences(summary):
#                           print sentence
#                           sentence = cleanText(sentence)
#                           print sentence
# 
#                           subtopicsNew = classify(sentence)
#                           subtopics.extend(subtopicsNew)
#                           print subtopicsNew
# 
#                       #print subtopics
#                       vote.bill.subtopics = subtopics
#                       vote.bill.subtopicsAssigned=True
#                       vote.bill.save()
#                       print vote.bill.subtopics.all()
#                 elif (vote.bill and vote.bill.subtopicsAssigned) or (vote.amendment and vote.amendment.subtopicsAssigned):
#                       print 'ALREADY ASSIGNED HERE'
#                 else:
#                       print 'NO AMENDMENT AND NO BILL PURPOSE'
# 
# def findJonesSubTopicVotesSVMAll(sessionNum): 
#     for vote in Vote.objects.filter(bill__congress__number=sessionNum):   
#             findJonesSubTopicVotesSVM(vote)
#          
# def findJonesSubTopicVotesSVMAllTest():
#     vote = Vote.objects.filter(bill__congress__number=111,bill__number=3217,number=156)[0]
#     vote.amendment.subtopics=[]
#     vote.amendment.subtopicsAssigned=False
#     vote.amendment.save()
#     #print vote.amendment.subtopicsAssigned
#     
#     for vote in [vote]:
#             #print vote
#             #print vote.amendment.subtopicsAssigned
#             findJonesSubTopicVotesSVM(vote)
#             print 'HERE'
#             print vote.amendment.subtopics.all()
# 
# def findCloseVotes():
#     for av in AnomVoters.objects.all():
#         print av.vote
#         numDemAVS = av.demVoters.all().count()
#         numRepAVS = av.repVoters.all().count()
#         numAll = av.vote.numPresent + av.vote.numAye + av.vote.numNay + av.vote.numNV
#         if av.vote.percentGotten > av.vote.percentNeeded:
#             continue
# 
#         if numDemAVS > 0:
#             if av.demVoters.all()[0].voteCast == 'AYE':
#                 if ((numDemAVS + av.vote.numNay) / float(numAll)) > av.vote.percentNeeded:
#                     av.vote.demPossTurn=True
#                     print 'INFLUENCED VOTE DEM AYE'
#                     print (numDemAVS + av.vote.numNay) / float(numAll)
#                     print av.vote.percentGotten
#                     print av.vote.percentNeeded
#                     if (numDemAVS-1+av.vote.numNay) / float(numAll) < av.vote.percentNeeded:
#                         av.vote.demExact=True
#                         print 'EXACT'
#                     av.vote.save()
# 
#             elif av.demVoters.all()[0].voteCast == 'NAY':
#                 if ((numDemAVS + av.vote.numAye) / float(numAll)) > av.vote.percentNeeded:
#                     av.vote.demPossTurn=True
#                     print 'INFLUENCED VOTE DEM NAY'
#                     print (numDemAVS + av.vote.numAye) / float(numAll)
#                     print av.vote.percentGotten
#                     print av.vote.percentNeeded
#                     if ((numDemAVS - 1 + av.vote.numAye) / float(numAll)) < av.vote.percentNeeded:
#                        print 'EXACT'
#                        av.vote.demExact=True 
#                     av.vote.save()
# 
#         if numRepAVS > 0:
#             if av.repVoters.all()[0].voteCast == 'AYE':
#                 if ((numRepAVS + av.vote.numNay) / float(numAll)) > av.vote.percentNeeded:
#                     print 'INFLUENCED VOTE REP AYE'
#                     print (numRepAVS + av.vote.numNay) / float(numAll)
#                     print av.vote.percentGotten
#                     print av.vote.percentNeeded
#                     av.vote.repPossTurn=True
#                     if ((numRepAVS - 1 + av.vote.numNay) / float(numAll)) < av.vote.percentNeeded:
#                         print 'EXACT'
#                         av.vote.repExact=True
#                     av.vote.save()
# 
#             elif av.repVoters.all()[0].voteCast == 'NAY':
#                 if ((numRepAVS + av.vote.numAye) / float(numAll)) > av.vote.percentNeeded:
#                     print 'INFLUENCED VOTE REP NAY'
#                     print (numRepAVS + av.vote.numAye) / float(numAll)
#                     print av.vote.percentGotten
#                     print av.vote.percentNeeded
#                     av.vote.repPossTurn=True
#                     if ((numRepAVS - 1 + av.vote.numAye) / float(numAll)) < av.vote.percentNeeded:
#                         print 'EXACT'
#                         av.vote.repExact=True
#                     av.vote.save()

def generateVoteDescripts(session):
    #TODO: CHANGE FROM HOUSE TO SENATE, VICE VERSA
    for i,vote in enumerate(Vote.objects.filter(Q(bill__congress__number=session,senateVote=False)|Q(amendment__bill__congress__number=session,senateVote=False))):
        vote.htmlDescript = describeVoteSimple(vote)
        vote.save()
        print i
        
if __name__ == '__main__':
    downloadVotes(112)
    #generateVoteDescripts(111)
    #generateVoteDescripts(112)
    
    
from ccu_utilities import *
from ccu_gen_beta.models import *
import pyUtilities as pyU
from prediction3 import classify

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

def findJonesSubTopicVotesUnique(vote):
            print vote
            if vote.amendment:
                #use text of amendment to find subtopics....
                amendmentText = None
                if not genericAmendText(vote.amendment.purpose):
                    amendmentText = vote.amendment.purpose
                else:
                    return

                if not genericAmendText(vote.amendment.description) and amendmentText != vote.amendment.description:
                    amendmentText = amendmentText + ' ' + vote.amendment.description

                if vote.amendment.text and not genericAmendText(vote.amendment.text):
                    amendmentText = amendmentText + ' ' + vote.amendment.text

                if not amendmentText:
                    return

                amendmentText = amendmentText.split('as follows')[0]    

                #get all topics of bill to kind of narrow things down a bit....
                subjects = vote.bill.subjects.all()
                topics = []
                for subject in subjects:
                    for subtopic in subject.subtopics.all():
                        if subtopic.topic not in topics:
                            #print subtopic
                            topics.append(subtopic.topic)

                if topics == []: return

                subtopicsD = findJonesSubTopicPresUniqueWords(amendmentText,topics,score=0.14)
                print subtopicsD

            elif vote.bill.summary.strip() != "": #if aboutBillOrRes(vote.voteType.voteType)s:
                   #print 'HERE'
                   vote.subtopics = []
                   #just assign all subtopics of the bill to the vote...
                   lsSubtopics = []
                   topics = []
                   for subject in vote.bill.subjects.all():
                       #print 'SUBJECT %s' % subject
                       for subtopic in subject.subtopics.all():
                           #print '     SUBTOPIC %s w/ topic %s' % (subtopic.name,subtopic.topic.name)
                           if subtopic not in lsSubtopics:
                               lsSubtopics.append(subtopic)
                           if subtopic.topic not in topics:
                               topics.append(subtopic.topic)
                   #print vote.bill.summary
                   #print topics
                   subtopicsD = findJonesSubTopicPresUniqueWords(vote.bill.summary,topics,score=0.14)
                   #print subtopicsD
                   sameAsLast=True
                   print subtopicsD




def findJonesSubTopicVotes(vote):
        print vote
        if vote.amendment:
            #use text of amendment to find subtopics....
            amendmentText = None
            if not genericAmendText(vote.amendment.purpose):
                amendmentText = vote.amendment.purpose
            else:
                return
            
            if not genericAmendText(vote.amendment.description) and amendmentText != vote.amendment.description:
                amendmentText = amendmentText + ' ' + vote.amendment.description
            
            if vote.amendment.text and not genericAmendText(vote.amendment.text):
                amendmentText = amendmentText + ' ' + vote.amendment.text
            
            if not amendmentText:
                return
                
            amendmentText = amendmentText.split('as follows')[0]    
            
            #get all topics of bill to kind of narrow things down a bit....
            subjects = vote.bill.subjects.all()
            topics = []
            for subject in subjects:
                for subtopic in subject.subtopics.all():
                    if subtopic.topic not in topics:
                        #print subtopic
                        topics.append(subtopic.topic)
            
            if topics == []: return
            
            subtopicsD = findJonesSubTopicPres(amendmentText,topics,score=0.14)
            print subtopicsD
        
        elif vote.bill.summary.strip() != "": #if aboutBillOrRes(vote.voteType.voteType)s:
               #print 'HERE'
               vote.subtopics = []
               #just assign all subtopics of the bill to the vote...
               lsSubtopics = []
               topics = []
               for subject in vote.bill.subjects.all():
                   #print 'SUBJECT %s' % subject
                   for subtopic in subject.subtopics.all():
                       #print '     SUBTOPIC %s w/ topic %s' % (subtopic.name,subtopic.topic.name)
                       if subtopic not in lsSubtopics:
                           lsSubtopics.append(subtopic)
                       if subtopic.topic not in topics:
                           topics.append(subtopic.topic)
               #print vote.bill.summary
               #print topics
               subtopicsD = findJonesSubTopicPres(vote.bill.summary,topics,score=0.14)
               #print subtopicsD
               sameAsLast=True
               print subtopicsD

def cleanText(text):
    import string
    
    words= ['strike','year','resolut','legis','table','bill','pass','amend','title','subtitle','specif','author','prohibit','juris','respons','submit','enhance','include','publish','requir','set']
    words.extend(['add','continue','event','purpose','remov','establ','instruct','develop','designate','direct','provide','senate'])
    words.extend(['congress','report','plan','exclude','confirm','forth','includ','consider','secretar','report','implemen'])
    words.extend(['h.r.','section','sub','date','act','regard','earli','early','use','certain','west','east','north','south','clarify','propos','nation'])
    words.extend(['introduc','approp','admin','process','affect','promote','program','prescribe','assist','reduce','facilit','communit','committee','project'])
    words.extend(['revis','improv','increase','likel','carry','assoc','agree','control','develop','service','approv','program','participate','make','recommend','change','integra'])
    #words.extend(['incr','limit','def','revis','alloc','program','leverag','provid','encourag','meet','federal','nation'])
    words.extend(['primar'])
    
    text = text.lower()
    text = text.split('as follows')[0]
    reTitle1 = re.compile('mr.\s*\S*,',re.I)
    reTitle2 = re.compile('ms.\s*\S*,',re.I)
    reTitle3 = re.compile('mrs.\s*\S*,',re.I)
    reParen = re.compile("\(.*?\)")
    reNum = re.compile('\d+')
    
    text = re.sub(reTitle1,' ',text)
    text = re.sub(reTitle2,' ',text)
    text = re.sub(reTitle3,' ',text)
    text = re.sub(reParen,'' ,text)
    text = re.sub(reNum,'',text)
    text = text.replace('mr.','').replace('ms.','').replace('mrs.','')
    
    for rep in Rep.objects.all():
        text = text.replace(rep.lastName.lower(),'')
    
    
    for word in words:
        reWord = re.compile('\s+' + word + '\w*\s*')
        text = re.sub(reWord,' ',text)

    for stateName in stateAbbrevs.values():
        reWord = re.compile(stateName + '\w*\s*',re.I)
        text = re.sub(reWord,'',text)

    #print 'after statenames'
    #print text
    text = pyU.removePunctuation(text)
    text = pyU.sStripStopWordsAll(text)    
    #print 'after punc and strip words'
    #print text
    return text       

#ADD SOMETHING WHEN BILL OR AMENDMENT HAS ALREADY BEEN PROCESSED...
def findJonesSubTopicVotesSVM(vote):
    
        print ""
        print ""
        print "------------------------------------------"
        print vote
        #if vote.amendment:
            #vote.amendment.subtopicsAssigned=False
        #if vote.bill:
            #vote.bill.subtopicsAssigned=False
      
        if vote.amendment and not vote.amendment.subtopicsAssigned:
            #return
            #use text of amendment to find subtopics....
            amendmentText = None
            if not genericAmendText(vote.amendment.purpose):
                amendmentText = vote.amendment.purpose
            else:
                print 'generic amendment'
                print vote.amendment.purpose
                return

            if not genericAmendText(vote.amendment.description) and amendmentText != vote.amendment.description:
                amendmentText = amendmentText + ' ' + vote.amendment.description

            if vote.amendment.text and not genericAmendText(vote.amendment.text):
                amendmentText = amendmentText + ' ' + vote.amendment.text

            if not amendmentText:
                print 'no amendment text'
                return

            print 'AMENDMENT'
            print amendmentText
            amendmentText = cleanText(amendmentText)
            print "---------------"
            print amendmentText
            subtopics = classify(amendmentText)
            #print subtopics
            
            vote.amendment.subtopics = subtopics
            vote.amendment.subtopicsAssigned=True
            vote.amendment.save()
            print vote.amendment.subtopics.all()


        elif vote.bill.summary.strip() != "" and not vote.bill.subtopicsAssigned: #if aboutBillOrRes(vote.voteType.voteType)s:
              subjects = vote.bill.subjects.all()
              topics = []
              for subject in subjects:
                  for subtopic in subject.subtopics.all():
                      if subtopic.topic not in topics:
                          #print subtopic
                          topics.append(subtopic.topic)
             
              print 'BILL'
              
              summary = vote.bill.summary
              if len(summary) > 5000:
                  summary = summary[0:5000]
              print summary
              print "----------------------"
              #print len(vote.bill.summary)
              
              subtopics = []
              for sentence in pyU.lsSplitIntoSentences(summary):
                  print sentence
                  sentence = cleanText(sentence)
                  print sentence
              
                  subtopicsNew = classify(sentence)
                  subtopics.extend(subtopicsNew)
                  print subtopicsNew
                  
              #print subtopics
              vote.bill.subtopics = subtopics
              vote.bill.subtopicsAssigned=True
              vote.bill.save()
              print vote.bill.subtopics.all()
        elif (vote.bill and vote.bill.subtopicsAssigned) or (vote.amendment and vote.amendment.subtopicsAssigned):
              print 'ALREADY ASSIGNED'
        else:
              print 'NO AMENDMENT AND NO BILL PURPOSE'

              
def getSenatorsCongressSubtopic(congress,subtopicID):
      strSenators=""
      lsTrack=[]   
      for rep in Rep.objects.filter(senator=True,congress__number=congress).order_by('lastName'):
         obj1 = None
         obj2 = None
         obj3 = None
         obj4 = None
         #print rep.party
         if rep.party.lower().find('d') > -1:
             obj1 = AnomVoters.objects.filter(vote__bill__congress=congress,demVoters__rep=rep,vote__bill__subtopics__code=subtopicID)
             obj2 = AnomVoters.objects.filter(vote__bill__congress=congress,demVoters__rep=rep,vote__amendment__subtopics__code=subtopicID)
         else:
             obj3 = AnomVoters.objects.filter(vote__bill__congress=congress,repVoters__rep=rep,vote__bill__subtopics__code=subtopicID)
             obj4 = AnomVoters.objects.filter(vote__bill__congress=congress,repVoters__rep=rep,vote__amendment__subtopics__code=subtopicID)    

         print rep
         print obj1
         if obj1 != None:
             print 'HERE'
         print obj2
         print obj3
         print obj4
         print ""
         if (obj1 and obj1.count() == 0 and obj2.count() == 0) or (obj3 and obj3.count() == 0 and obj4.count() == 0):
              continue

         if rep.repID not in lsTrack:
             strSenators = strSenators + ("%s:%s*" % (rep.repID,rep.lastName))
             lsTrack.append(rep.repID)

      return strSenators




if __name__ == '__main__':
    print getSenatorsCongressSubtopic(112,1911)
    # from JulianTime import convertDateTimeJul
    #     congress112 = Congress.objects.filter(number=112)[0]
    #     dtObj1 = congress112.beginDate
    #     dtObj1 = datetime.datetime(dtObj1.year,dtObj1.month,dtObj1.day)
    #     dtObj2 = congress112.endDate
    #     dtObj2 = datetime.datetime(dtObj2.year,dtObj2.month,dtObj2.day)
    #     print convertDateTimeJul(dtObj1)
    #     print convertDateTimeJul(dtObj2)
    #     assert 0
    #     
    #print NAICSIndustryReport.objects.filter(vote=Vote.objects.get(number=288,bill__number=3082))
    
    #pass
    #for vote in Vote.objects.filter(bill__congress__number=112):
        #findJonesSubTopicVotesSVM(vote)
        
    #for vote in Vote.objects.filter(bill__congress__number=111):
        #findJonesSubTopicVotesSVM(vote)
       
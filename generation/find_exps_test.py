from ccu_gen_beta.models import *
import simplejson
from ccu_utilities import *
from datetime import date,timedelta
from django.db.models import *
import numpy
from django.utils.encoding import smart_str

def isPVIOutlier(statePVI,rep,vote):
    #find statepvi here...
    
    allScores = []
    allStates = []
    for stObj in StatePVI.objects.filter(year=statePVI.year):
        otherReps = Rep.objects.filter(state=stObj.state,congress=rep.congress)
        found=False
        for repOther in otherReps:
            if found==True: break
            if repOther.party == rep.party:
                score = stObj.scoreCook
                if not stObj.demCook:
                    score = 0 - score
                
                allScores.append(score)
                allStates.append(stObj.state)
    
    mainScore = statePVI.scoreCook
    if not statePVI.demCook:
        mainScore = 0-mainScore

    isOut,typeOut = isOutlier(mainScore,allScores)
    if isOut:
        return isOut,typeOut,numpy.mean(allScores)
    else:
        return isOut,typeOut,None

def findStatePVI(rep,vote):
    
    try:
        print rep
        print vote
    except Exception,ex:
        pass
        
    if StatePVIReport.objects.filter(rep=rep,vote=vote).count() > 0:
        return
        
    statePVI = StatePVI.objects.filter(state=rep.state,year__lt=vote.dateVote.year).order_by('-year')
    if statePVI.count() == 0 or not statePVI:
        statePVI = StatePVI.objects.filter(state=rep.state).order_by('-year')

    statePVI = statePVI[0]
        
    isOut,typeOut,avg = isPVIOutlier(statePVI,rep,vote)
    print rep.party
    print isOut
    print typeOut
    if rep.party=='D':
        print 'HERE'
        if isOut and typeOut.lower().find('low') > -1:
            print 'REP %s state PVI report' % rep
            StatePVIReport.objects.get_or_create(statePVI=statePVI,rep=rep,vote=vote,averageScore=avg)
    elif rep.party == 'R':
        print 'HERE'
        if isOut and typeOut.lower().find('high') > -1:
            print 'REP %s state PVI report' % rep
            StatePVIReport.objects.get_or_create(statePVI=statePVI,rep=rep,vote=vote,averageScore=avg)
    
def biPartisanVoter(rep,vote):
    if RepWithPartyReport.objects.filter(vote=vote,repWithParty__rep=rep).count() > 0:
          return
    
    try:
       rwObj = RepWithParty.objects.get(rep=rep)
    except Exception:
       return
    
    congress = rep.congress
    if congress.number not in partyPercentD:
        addPartyPercentD(congress.number)
  
    isOut,typeOut = isOutlier(rwObj.withPartyScore,partyPercentD[congress.number])
        
    if isOut and typeOut=='LOW':
         rwv = RepWithPartyReport.objects.get_or_create(repWithParty=rwObj,vote=vote)

def lookUpChoice(text,choice):
     for item in choice:
         if item[0] == text:
             return item[1]
     return None

def nextElectionRep(rep,vote):
     if PredElectionReport.objects.filter(vote=vote,predElection__rep=rep).count() > 0:
           return
    
     pes = PredElection.objects.filter(rep=rep,date__lte=vote.dateVote).order_by('-date')

     pe = None
     if pes.count() > 0: pe= pes[0]
     else:return
    
     #if election is over a year away don't worry about it
     timeApart = pe.election.date - vote.dateVote
     if abs(timeApart.days) > 365:
         return

     pred = pe.pred

     found = False
     if rep.party=='R' and pred in ['SOLID_D','LIKE_D','LEAN_D','TU','LEAN_R']:
         found=True

     elif rep.party=='D' and pred in ['SOLID_R','LIKE_R','LEAN_R','TU','LEAN_D']:
         found=True

     elif pred in ['RS','RG','RM','PR','PS','PG','PM']:
         found=True

     if found:
         per = PredElectionReport.objects.get_or_create(predElection=pe,vote=vote) 
         print 'ELECTION REPORT SAVED'

def findCommitteeChair(voter,vote):
      if ChairCommitteeReport.objects.filter(vote=vote,rep=voter).count() > 0:
          return
    
      if vote.amendment and vote.amendment.subtopics.all().count() == 0:
             print 'NO SUBTOPICS FOR VOTE IN COMMITTEES'
             return
      elif vote.bill and vote.bill.subtopics.all().count()==0:
             print 'NO SUBTOPICS FOR VOTE IN COMMITTEES'
             return
      voteTopics = []
      if vote.amendment:
            subtopics = vote.amendment.subtopics.all()
      else:
            subtopics = vote.bill.subtopics.all()

      
      for st in subtopics:
          if st.topic not in voteTopics:
              voteTopics.append(st.topic)

      relComms = Committee.objects.filter(topics__in=voteTopics,chair=voter)
      if len(relComms) > 0:
          for comm in relComms:
             ChairCommitteeReport.objects.get_or_create(committee=comm,rep=voter,vote=vote)

      relComms = Committee.objects.filter(topics__in=voteTopics,viceChair=voter)
      if len(relComms) > 0:
          for comm in relComms:
             ChairCommitteeReport.objects.get_or_create(committee=comm,rep=voter,vote=vote)

      relComms = Committee.objects.filter(topics__in=voteTopics,rankingMember=voter)
      if len(relComms) > 0:
          for comm in relComms:
             ChairCommitteeReport.objects.get_or_create(committee=comm,rep=voter,vote=vote) 

def findRelIndustries(voter,vote):
     #if NAICSIndustryReport.objects.filter(vote=vote,rep=voter).count() > 0:
         #return 
    
     if vote.amendment and vote.amendment.subtopics.all().count() == 0:
           print 'NO SUBTOPICS FOR VOTE IN INDUSTRIES'
           return
     elif vote.bill and vote.bill.subtopics.all().count()==0:
           print 'NO SUBTOPICS FOR VOTE IN INDUSTRIES'
           return

     if vote.amendment:
          subtopics = vote.amendment.subtopics.all()
     else:
          subtopics = vote.bill.subtopics.all()
    
     print subtopics
     industries = list(set([nai.naicsIndustry for nai in NAICS_Locale.objects.filter(state=voter.state,naicsIndustry__subtopics__in=subtopics)]))
     print 'INDUSTRIES TO LOOK AT'
     print industries
     for industry in industries:
         #try:
         voterIndustry = NAICS_Locale.objects.filter(naicsIndustry=industry,state=voter.state).order_by('-endYear')[0]
         #except Exception,ex:
            # print ex
             
             
         percentEmps = voterIndustry.percentage()
         strLookup = getLookupStrInd(voterIndustry)
         if not strLookup in industryPercentD:
              addIndustryPercentD(voterIndustry)
         isOut,typeOut= isOutlier(percentEmps,industryPercentD[strLookup])
         print isOut
         print typeOut
         if isOut and typeOut.find('HIGH') > -1:
             print 'ABOUT TO SAVE INDUSTRY'
             ir = NAICSIndustryReport.objects.get_or_create(vote=vote,rep=voter,naicsLocale=voterIndustry)[0]
             ir.rank = len(industryPercentD[strLookup]) - industryPercentD[strLookup].index(percentEmps)
             print voterIndustry
             print percentEmps
             print ir.rank
             print 'INDUSTRY REPORT SAVED'
             ir.save()
             
def findRelContrs(voter,vote): 
     if vote.amendment and vote.amendment.subtopics.all().count() == 0:
          print 'NO SUBTOPICS FOR VOTE IN CONTRIBUTION'
          return
     elif vote.bill and vote.bill.subtopics.all().count()==0:
          print 'NO SUBTOPICS FOR VOTE IN CONTRIBUTION'
          return
     
     if RepContributionReport.objects.filter(vote=vote,rep=voter).count() > 0:
         return
     
     mlBuses = []
     mlCite = []
     orgUsed = False

     if vote.amendment:
         mlBuses = list(MapLightBusiness.objects.filter(subtopics__in=vote.amendment.subtopics.all()))
     else:
         mlBuses = list(MapLightBusiness.objects.filter(subtopics__in=vote.bill.subtopics.all()))
     
     #make sure businesses are unique
     mlBuses = list(set(mlBuses))
     mlBuses = [bus for bus in mlBuses if bus.name.find('Republican') == -1 and bus.name.find('Democrat') == -1]
     print "MAP LIGHT BUSES TO LOOK AT"
     print mlBuses
     for i,bus in enumerate(mlBuses):
         rcVoter = RepContribution.objects.filter(rep=voter,dateContr__lte=vote.dateVote,mlBusiness=bus).order_by('dateContr')
         if  rcVoter.count() > 0:
             totalAmt = rcVoter.aggregate(Sum('amountContr'))['amountContr__sum']
             oldDate = rcVoter[0].dateContr
             lookupStr = getLookUpStrContr(vote,bus,oldDate)
             print lookupStr
             lsTotalAmt = []
             if not lookupStr in contrD:
                 addContrD(vote,voter,bus,oldDate)
               
             lsTotalAmt = contrD[lookupStr]
             try:
                 print smart_str(voter)
                 print totalAmt
             except Exception,ex:
                 print ex
                 pass

             if totalAmt > 10000:
                 isOut,typeOut = isOutlier(totalAmt,lsTotalAmt)
                 if isOut and typeOut.find('HIGH') > -1:
                     #rc = RepContributionReport.objects.get_or_create(endDate=vote.dateVote,mlBusiness=bus,vote=vote,rep=voter,orgStanceMapping=orgUsed)[0]
                     rc = RepContributionReport.objects.get_or_create(startDate=oldDate,endDate=vote.dateVote,mlBusiness=bus,vote=vote,rep=voter,orgStanceMapping=orgUsed)[0]
                     rc.rank=len(lsTotalAmt) - lsTotalAmt.index(totalAmt)
                     rc.save()
                     print 'REP CONTRIBUTION REPORT MADE'
                     
def findAllReasons(rep,vote):
    #findStatePVI(rep,vote)
    #biPartisanVoter(rep,vote)         
    #nextElectionRep(rep,vote)      
    #findCommitteeChair(rep,vote)
    findRelIndustries(rep,vote)
    #findRelContrs(rep,vote)
    
def findExps(vote):
     try:
         avObj = AnomVoters.objects.get(vote=vote)
         #print avObj
     except Exception,ex:
         print 'EXCEPTION...'
         print ex
         #print "NO OBJ FOR %s " % vote
         return

     demVoters = [dv.rep for dv in avObj.demVoters.all().order_by('rep__lastName')]
     repVoters = [rv.rep for rv in avObj.repVoters.all().order_by('rep__lastName')]
     if len(demVoters) == 0 and len(repVoters)==0:
         print 'NO ANOM VOTERS'
     
     for voter in demVoters:
         if voter.senator:
             print voter
             findAllReasons(voter,vote)
     for voter in repVoters: 
         if voter.senator:
             print voter
             findAllReasons(voter,vote)

def findAllExps(session):
    for vote in Vote.objects.filter(bill__congress__number=session).order_by('-dateVote'):
          try:
              print vote
              print vote.dateVote
              if vote.amendment:
                  print vote.amendment.subtopics.all()
              print vote.bill.subtopics.all()
              print ""
              #print describeVote(vote)
              findExps(vote)
              print ""
          except Exception,ex:
              print ex
              
def findExpsTest():
    for vote in Vote.objects.all():#Vote.objects.filter(bill__congress__number=111,bill__number=3217,number=156).order_by('-dateVote'):
          #try:
              print vote
              print vote.dateVote
              #print describeVote(vote)
              findExps(vote)
              print ""
          #except Exception,ex:
              #print ex
             
if __name__ == '__main__':
     findExpsTest()
#600
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

    try:
       statePVI = statePVI[0]
    except Exception:
       return
        
    isOut,typeOut,avg = isPVIOutlier(statePVI,rep,vote)
    print rep.party
    print isOut
    print typeOut
    if rep.party=='D':
        print 'HERE'
        if isOut and typeOut.lower().find('low') > -1:
            print 'REP %s state PVI report' % rep
            StatePVIReport.objects.get_or_create(statePVI=statePVI,rep=rep,vote=vote,averageScore=avg)
            vr,isThere = VoteReport.objects.get_or_create(vote=vote)
            vr.hasDiff=True
            vr.save()
    elif rep.party == 'R':
        print 'HERE'
        if isOut and typeOut.lower().find('high') > -1:
            print 'REP %s state PVI report' % rep
            StatePVIReport.objects.get_or_create(statePVI=statePVI,rep=rep,vote=vote,averageScore=avg)
            vr,isThere = VoteReport.objects.get_or_create(vote=vote)
            vr.hasDiff=True
            vr.save()
          
def biPartisanTF(rep,vote):
    #if RepWithPartyReport.objects.filter(vote=vote,repWithParty__rep=rep).count() > 0:
          #return

    try:
       rwObj = RepWithParty.objects.get(rep=rep)
    except Exception,ex:
       #print 'REP WITH PARTY DOESN"T EXIST"'
       try:
           print rep
       except Exception,ex:
           pass
       return
       

    congress = rep.congress
    if congress.number not in partyPercentD:
        addPartyPercentD(congress.number)

    isOut,typeOut = isOutlier(rwObj.withPartyScore,partyPercentD[congress.number])

    if isOut and typeOut.find('LOW') > -1:
         return True
    else:
        return False

    
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
    print isOut
    print typeOut    
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
         vr,isThere = VoteReport.objects.get_or_create(vote=vote)
         vr.hasElec=True
         vr.save()
         print 'ELECTION REPORT SAVED'


def findCommitteeChair(voter,vote):
      #if ChairCommitteeReport.objects.filter(vote=vote,rep=voter).count() > 0:
          #return
    
      start = datetime.datetime.now()
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

      hasComm = False
      relComms = Committee.objects.filter(topics__in=voteTopics,chair=voter)
      if len(relComms) > 0:
          hasComm=True
          for comm in relComms:
             ChairCommitteeReport.objects.get_or_create(committee=comm,rep=voter,vote=vote)
             

      relComms = Committee.objects.filter(topics__in=voteTopics,viceChair=voter)
      if len(relComms) > 0:
          hasComm=True
          for comm in relComms:
             ChairCommitteeReport.objects.get_or_create(committee=comm,rep=voter,vote=vote)
            
      relComms = Committee.objects.filter(topics__in=voteTopics,rankingMember=voter)
      if len(relComms) > 0:
          hasComm=True
          for comm in relComms:
             ChairCommitteeReport.objects.get_or_create(committee=comm,rep=voter,vote=vote) 
          
      if hasComm:
          vr,isThere = VoteReport.objects.get_or_create(vote=vote)
          vr.hasComm=True
          vr.save() 
          
def findRelIndustries(voter,vote):

     
     #if NAICSIndustryReport.objects.filter(vote=vote,rep=voter).count() > 0:
         ##vr,isThere = VoteReport.objects.get_or_create(vote=vote)
         #vr.hasInd=True
         #vr.save()
         #return 
     start = datetime.datetime.now()
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
     
     if voter.state:
         state=voter.state
     else:
         state=voter.district.state
         
     industries = list(set([nai.naicsIndustry for nai in NAICS_Locale.objects.filter(state=state,naicsIndustry__subtopics__in=subtopics)]))
     print 'INDUSTRIES TO LOOK AT'
     print industries
     for industry in industries:
         #try:
         voterIndustry = NAICS_Locale.objects.filter(naicsIndustry=industry,state=state).order_by('-endYear')[0]
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
             #ir = NAICSIndustryReport.objects.get_or_create(vote=vote,rep=voter,naicsLocale=voterIndustry,rank=0)[0]
             #ir.rank = len(industryPercentD[strLookup]) - industryPercentD[strLookup].index(percentEmps)
             #print voterIndustry
             #print percentEmps
             #print ir.rank
             print 'INDUSTRY REPORT SAVED'
             #ir.save()
     
             vr,isThere = VoteReport.objects.get_or_create(vote=vote)
             vr.hasInd=True
             vr.save()     
     end = datetime.datetime.now()
     delta = end-start
     print delta.seconds
     print delta.microseconds
     assert 0   

def findRelCompanyContrs(voter,vote):
      print "VOTE VOTER"
      print vote
      try:
          print voter
      except Exception:
          pass
      
      
      if RepContributionReport.objects.filter(vote=vote,rep=voter).count() == 0:
          print 'NO REP CONTRIBUTIONS IN COMPANY - RETURNING'
          return
          
      if vote.amendment and vote.amendment.subtopics.all().count() == 0:
           print 'NO SUBTOPICS FOR VOTE IN CONTRIBUTION'
           return
      elif vote.bill and vote.bill.subtopics.all().count()==0 and vote.bill.orgStances.all().count()==0:
           print 'NO SUBTOPICS FOR VOTE IN CONTRIBUTION'
           return

      print "NUMBER OF REPORTS %d" % RepContributionReport.objects.filter(vote=vote,rep=voter).count()
      for rcr in RepContributionReport.objects.filter(vote=vote,rep=voter):
           rcr.orgStancesAgainst=[]
           rcr.orgStancesFor=[]
           rcr.amtMoneyFor=0
           rcr.amtMoneyAgainst=0
           rcr.relRCSFor=[]
           rcr.relRCSAgainst=[]
           rcr.save()
           RepOrgStanceMoneyVote.objects.filter(repReport=rcr).delete()
           
           
          
           if RepOrgStanceMoneyVote.objects.filter(repReport=rcr).count() > 0:
               return
          
           bus = rcr.bus
           orgStancesFor = [orgStance for orgStance in vote.bill.orgStances.all() if orgStance.against==False and orgStance.org.mlBusiness==bus]
           orgStancesAgainst=[orgStance for orgStance in vote.bill.orgStances.all() if orgStance.against==True and orgStance.org.mlBusiness==bus]
           rcr.orgstancesFor = orgStancesFor
           rcr.orgstancesAgainst = orgStancesAgainst
           rcr.save()
           print "ORG STANCES FOR AND AGAINST"
           try:
               print rcr.orgstancesFor.all()
               print rcr.orgstancesAgainst.all()
           except Exception,ex:
               pass
           allRCS = rcr.rcs.all()

           for orgst in orgStancesFor:
                lsOrgStanceName=[orgst.org.orgName]
                ots  = OrgName.objects.filter(org=orgst.org)
                if ots.count() > 0:
                   for ot in ots:
                       lsOrgStanceName.append(ot.name)

                rcsIndiv=[]
                for name in lsOrgStanceName:
                    rcsIndiv.extend(list(allRCS.filter(Q(contribName__iexact=name)|Q(contribEmployer__iexact=name))))
                
                rcr.relRCSFor = rcsIndiv
                rcr.save()    
                rcsAmount = sum([rc.amountContr for rc in rcsIndiv])
                rcr.amtMoneyFor = rcsAmount
                rcr.save()
                if len(rcsIndiv) > 0:
                   rsm,there = RepOrgStanceMoneyVote.objects.get_or_create(repReport=rcr,orgst=orgst,totalAmt=rcsAmount,forVote=True)
                   rsm.rcs=rcsIndiv
                   rsm.save()
                   try:
                       print rsm.totalAmt
                   except Exception:
                       pass

           for orgst in orgStancesAgainst:
                    lsOrgStanceName=[orgst.org.orgName]
                    ots  = OrgName.objects.filter(org=orgst.org)
                    if ots.count() > 0:
                       for ot in ots:
                           lsOrgStanceName.append(ot.name)

                    rcsIndiv=[]
                    for name in lsOrgStanceName:
                        rcsIndiv.extend(list(allRCS.filter(Q(contribName__iexact=name)|Q(contribEmployer__iexact=name))))
                    
                    rcr.relRCSAgainst = rcsIndiv
                    rcr.save()
                    rcsAmount = sum([rc.amountContr for rc in rcsIndiv])
                    rcr.amtMoneyAgainst = rcsAmount
                    rcr.save()
                    if len(rcsIndiv) > 0:
                       rsm,there = RepOrgStanceMoneyVote.objects.get_or_create(repReport=rcr,orgst=orgst,totalAmt=rcsAmount,forVote=False)
                       rsm.rcs=rcsIndiv
                       rsm.save()
                       vr = VoteReport.objects.get_or_create(vote=vote)[0]
                       vr.hasStance=True
                       vr.save()
                       try:
                           print rsm.totalAmt
                       except Exception:
                           pass
      
              
def findRelContrs2(voter,vote): 
      #if RepContributionReport.objects.filter(rep=voter,vote=vote)[:1].count() > 0:
          #print 'FOUND REP CONTR REPORT'
          #return
      start = datetime.datetime.now()    
      #find all subtopics
      if vote.amendment and vote.amendment.subtopics.all().count() == 0:
           print 'NO SUBTOPICS FOR VOTE IN CONTRIBUTION'
           return
      elif vote.bill and vote.bill.subtopics.all().count()==0 and vote.bill.orgStances.all().count()==0:
           print 'NO SUBTOPICS FOR VOTE IN CONTRIBUTION'
           return
           
      
      #find businesses/sectors involved
      mlBuses = []
      mlSectors = []
      if vote.amendment:
          mlBuses = list(MapLightBusiness.objects.filter(subtopics__in=vote.amendment.subtopics.all()))
          orgStances = vote.amendment.bill.orgStances.all()
      else:
          mlBuses = list(MapLightBusiness.objects.filter(subtopics__in=vote.bill.subtopics.all()))
          orgStances = vote.bill.orgStances.all()
          mlBuses.extend([orgst.org.mlBusiness for orgst in orgStances])

      dSector = {}
      for bus in mlBuses:
          if bus.name.lower().find('republican')==-1 and bus.name.lower().find('democrat')==-1:
              if bus.industry.sector not in dSector.keys():
                  dSector[bus.industry.sector] = [bus]
              else:
                  dSector[bus.industry.sector].append(bus)
      
      print "MAP LIGHT SECTORS TO LOOK AT"
      print dSector
      
      for sector,sector_buses in dSector.items():
          print ""
          print sector
          
          totalAmtSector = 0
          for bus in sector_buses:
              print bus
              print 'FINDING TOTAL AMT BUS'
              print totalAmtSector
              lsBus = RepContributionTotalAmountsBus.objects.filter(rep=voter,endDate__lte=vote.dateVote,bus=bus)
              if lsBus.count() > 0:
                  if lsBus.latest('endDate').endDate==vote.dateVote:
                      totalAmtSector+=lsBus.latest('endDate').totalAmt
                  else:
                      totalAmt1 = lsBus.latest('endDate').totalAmt
                      tb = RepContributionTotalAmountsBus()
                      tb.bus=bus
                      rcs = RepContribution.objects.filter(rep=voter,dateContr__gte=lsBus.latest('endDate').endDate,dateContr__lte=vote.dateVote,mlBusiness=bus)
                      if rcs.count() > 0:
                          tb.totalAmt = totalAmt1 + rcs.aggregate(Sum('amountContr'))['amountContr__sum']
                      else:
                          tb.totalAmt = totalAmt1
                          
                      tb.rep=voter
                      tb.endDate = vote.dateVote
                      rcs2 = list(lsBus.latest('endDate').rcs.all())
                      rcs2.extend(rcs)
                      tb.save()
                      tb.rcs=rcs2
                      tb.save()
                      totalAmtSector+=tb.totalAmt
              else:          
                    tb = RepContributionTotalAmountsBus()
                    tb.bus=bus
                    rcs = RepContribution.objects.filter(rep=voter,dateContr__lte=vote.dateVote,mlBusiness=bus)
                    if rcs.count() > 0:
                        tb.totalAmt = rcs.aggregate(Sum('amountContr'))['amountContr__sum']
                        tb.rep=voter
                        tb.endDate = vote.dateVote
                        tb.save() 
                        tb.rcs=rcs
                        tb.save()
                        totalAmtSector+=tb.totalAmt
                    else:
                        continue
                        
          #find total amount for percentage (totalAmountsBus all buses/totalAmounts)...    
          if totalAmtSector > 0:                
              print 'FINDING TOTAL'
              lsTIA = RepContributionTotalAmounts.objects.filter(rep=voter,endDate__lte=vote.dateVote)
          
              totalAmtInAll = None
              if lsTIA.count() > 0:
                  if lsTIA.latest('endDate').endDate==vote.dateVote:
                      print 'FOUND TOTAL AMOUNT'
                      totalAmtInAll = lsTIA[0].totalAmt
                      print totalAmtInAll
                  else:
                      rcs = RepContribution.objects.filter(rep=voter,dateContr__gte=lsTIA[0].endDate)
                      totalAmt1 = rcs.aggregate(Sum('amountContr'))['amountContr__sum']
                      if not totalAmt1:
                          totalAmt1 = 0
                          
                      totalAmtInAll = lsTIA.latest('endDate').totalAmt + totalAmt1
                      print totalAmtInAll
                      rct = RepContributionTotalAmounts(totalAmt=totalAmtInAll,endDate=vote.dateVote,rep=voter)
                      rct.save()
                      rct.rcs = rcs
                      rct.save()
              else:
                  rcs = RepContribution.objects.filter(rep=voter,dateContr__lte=vote.dateVote)
                  totalAmtInAll=0
                  if len(rcs) > 0:
                      totalAmtInAll = rcs.aggregate(Sum('amountContr'))['amountContr__sum']
                      print totalAmtInAll
                      rct = RepContributionTotalAmounts.objects.get_or_create(rep=voter,endDate=vote.dateVote,totalAmt=totalAmtInAll)
                      rct[0].rcs=rcs
                      rct[0].save()
          else:
              continue
          
          
          print totalAmtSector/float(totalAmtInAll)  
          if totalAmtSector/float(totalAmtInAll) > 0.08:
               #report
               for bus in sector_buses:
                    print "MAKING REP CONTRIBUTION REPORT FOR BUS"
                    print bus
                    rc_bus = RepContributionReport.objects.filter(bus=bus,rep=voter,vote=vote)
                    if rc_bus.count() > 0:
                        if rc_bus.latest('endDate').endDate < vote.dateVote:
                            totalAmt1 = rc_bus.latest('endDate').totalAmt
                            rcs = RepContribution.objects.filter(dateContr__gte=rc_bus.latest('endDate').endDate,dateContr__lte=vote.dateVote,rep=voter,mlBusiness=bus)
                            if rcs.count() == 0:
                                continue
                            totalAmt2 = rcs.aggregate(Sum('amountContr'))['amountContr__sum']
                            rc = RepContributionReportBus()
                            rc.totalAmt = totalAmt1+totalAmt2
                            rc.rep = voter
                            rc.vote=vote
                            rc.bus=bus
                            rc.endDate=vote.dateVote
                            lsRCS=rc_bus.latest().rcs.all()
                            lsRCS.extend(rcs)
                            rc.rcs = lsRCS
                            rc.save()
                            print rc
                        else:
                            print rc_bus    
                    else:
                        rcs = RepContribution.objects.filter(dateContr__lte=vote.dateVote,rep=voter,mlBusiness=bus)
                        if rcs.count() == 0:
                            continue
                            
                        totalAmt2 = rcs.aggregate(Sum('amountContr'))['amountContr__sum']
                        rc = RepContributionReport()
                        rc.totalAmt = totalAmt2
                        rc.rep = voter
                        rc.vote=vote
                        rc.bus=bus
                        rc.endDate=vote.dateVote
                        rc.save()
                        rc.rcs=rcs
                        rc.save()
                        try:
                            print rc
                        except Exception:
                             pass
                   
      end = datetime.datetime.now()
      delta = end-start
      print delta.seconds
      print delta.microseconds
      assert 0
               #vr = VoteReport.objects.get_or_create(vote=vote)[0]
               #vr.hasContr=True
               #vr.save()

def findAllReasons(rep,vote):
    
    #findStatePVI(rep,vote) #TODO
    #biPartisanVoter(rep,vote)  #TODO
    #nextElectionRep(rep,vote) 
    #findCommitteeChair(rep,vote)
    #findRelIndustries(rep,vote) 
    findRelContrs2(rep,vote)
    #findRelCompanyContrs(rep,vote) #TODO
    
def findExps(vote):
     try:
         avObj = AnomVoters.objects.get(vote=vote)
         #print avObj
     except Exception,ex:
         print 'EXCEPTION...'
         print ex
         #print "NO OBJ FOR %s " % vote
         return
     #start = datetime.datetime.now()
     demVoters = [dv.rep for dv in avObj.demVoters.all().order_by('rep__lastName') if not biPartisanTF(dv.rep,vote)]
     repVoters = [rv.rep for rv in avObj.repVoters.all().order_by('rep__lastName') if not biPartisanTF(rv.rep,vote)]
     end = datetime.datetime.now()
     #delta = end-start
     #print delta.seconds
     #print delta.microseconds
     #assert 0
     if len(demVoters) == 0 and len(repVoters)==0:
         print 'NO ANOM VOTERS'
              
     for voter in demVoters:
         findAllReasons(voter,vote)
     
     for voter in repVoters:
         findAllReasons(voter,vote)

def findAllExps(session):
    print(Vote.objects.all().count())
    for i,vote in enumerate(Vote.objects.all().order_by('-dateVote')):
              
              print vote
              print vote.dateVote
              if vote.amendment:
                  print 'AMENDMENT SUBTOPICS'
                  print vote.amendment.subtopics.all()
              
              print 'BILL SUBTOPICS'
              print vote.bill.subtopics.all()
              print ""

              findExps(vote)
              print ""
          #except Exception,ex:
              #print ex
              
def findExpsTest():
    #at 477 and 2454
    #lsVotes = [(117, 22), (104, 1106), (204, 1145), (187, 1256), (335, 1256), (139, 1388), (153, 146), (143, 1586), (182, 1664), (242, 1728), (477, 2454), (460, 2647), (314, 2751), (350, 2847), (404, 2847), (408, 2847), (991, 2847), (875, 2868), (297, 31), (718, 3221), (719, 3221), (687, 324), (728, 324), (722, 3548), (851, 3639), (909, 3961), (887, 3962), (194, 411), (968, 4173), (943, 4213), (651, 556), (310, 626), (291, 915)]
    #lsVotes = [(491, 1249), (459, 2112), (857, 2112), (162, 4), (126, 5), (164, 525), (33, 658), (791, 2250), (192, 3523), (923, 3630), (72, 3630), (96, 4105), (195, 4628), (177, 9)]
    lsVotes=[(875,2868)]
    for info_vote in lsVotes:
              vote = Vote.objects.filter(number=info_vote[0],bill__number=info_vote[1],senateVote=False,bill__congress__number=111)[0]
    #for vote in Vote.objects.filter(senateVote=False,number__in=lsVotes,bill__congress__number=111).order_by('-dateVote'):
          #try:
              print vote
              print vote.dateVote
              #print describeVote(vote)
              findExps(vote)
              print ""
          #except Exception,ex:
              #print ex

def assignPoints(session):
    #for i,vote in enumerate(Vote.objects.filter(bill__congress__number=111,bill__number=2868,number=875)):
    for i,vote in enumerate(Vote.objects.filter(Q(bill__congress__number=session)|Q(amendment__bill__congress__number=session))):

        allVoters = []
        try:
            allVoters = [av for av in AnomVoters.objects.get(vote=vote).demVoters.all().order_by('rep__lastName')]

        except Exception,ex:
            pass
            #print ex

        try:
            allVoters.extend([av for av in AnomVoters.objects.get(vote=vote).repVoters.all().order_by('rep__lastName')])
        except Exception:
            pass

        dPoints={} 
        for av in allVoters:   
            voter = av.rep
            out = biPartisanTF(voter,vote)
            if out:
                continue
            
            dPoints[voter]=0

            #PRED ELECTION POINTS
            pr = PredElectionReport.objects.filter(vote=vote,predElection__rep=voter)
            if pr.count() > 0:
                dPoints[voter]+=10
                     
            #STATE DIFF POINTS
            st = StatePVIReport.objects.filter(vote=vote,rep=voter)
            if st.count() > 0:
                st = st[0]
                dPoints[voter] += (abs(st.statePVI.scoreCook)+abs(st.averageScore))*5

            
            #CHAIR COMMITTEE POINTS
            ccs = ChairCommitteeReport.objects.filter(vote=vote,rep=voter)
            if ccs.count() > 0:
                dPoints[voter]+=50
            
            #LOCAL INDUSTRY POINTS        
            naicsObjs = NAICSIndustryReport.objects.filter(vote=vote,rep=voter)
            if naicsObjs.count() > 0:
                maxNAICS=0
                for no in naicsObjs:
                    if maxNAICS > (10*no.percentage()) or maxNAICS==0:
                        maxNAICS=(10*no.percentage())
                dPoints[voter]+=maxNAICS
                     
            #REP CONTRIBUTIONS
            rcs = RepContributionReport.objects.filter(vote=vote,rep=voter)
            sectors = list(set(rcs.values_list('bus__industry__sector',flat=True)))
            maxPercent=0

            for sector in sectors:
                rc_buses = rcs.filter(bus__industry__sector=sector)
                total = rc_buses.aggregate(Sum('totalAmt'))['totalAmt__sum']
                totalAll = RepContributionTotalAmounts.objects.filter(endDate=vote.dateVote,rep=voter)[0].totalAmt
                percent =  (total/float(totalAll))
                if percent*100 > maxPercent or maxPercent==0:
                    maxPercent = (total/float(totalAll))*100

            dPoints[voter] +=maxPercent 
           
            #COMPANY STANCES 
            if not vote.hasAmendment:
               for sector in sectors:
                  rc_buses = rcs.filter(bus__industry__sector=sector)
                  amtCompFor=0
                  amtCompAgainst=0
            
                  for rc in rc_buses: 
                       if rc.amtMoneyFor != None:
                           amtCompFor += rc.amtMoneyFor
                
                       if rc.amtMoneyAgainst!=None:
                           amtCompAgainst += rc.amtMoneyAgainst
                        
                  if amtCompFor>0:
                       print 'ADDING in COMP STANCE'
                       print i
                       print vote
                       try:
                          print voter
                       except Exception,ex:
                          pass
                       print amtCompFor
                       dPoints[voter]+= (amtCompFor)
                  if amtCompAgainst>0:
                       print 'ADDING IN COMP STANCE'
                       print i
                       print vote
                       try:
                          print voter
                       except Exception,ex:
                          pass
                       print amtCompAgainst
                       dPoints[voter]+= (amtCompAgainst)
                        
 
        #print dPoints  
        for rep,points in dPoints.items():
               tr = TempRepPoints.objects.filter(rep=rep,vote=vote)
               if tr.count() == 0:
                   tr = TempRepPoints()
                   tr.rep=rep
               else:
                   tr = tr[0]
                   
               tr.points=points
               if tr.points > 0:
                   if abs(vote.percentNeeded - vote.percentGotten) < .15: #close vote
                       percentAye = vote.numAye / float(vote.numAye+vote.numNay+vote.numPresent+vote.numNV)
                       percentNay = vote.numNay / float(vote.numAye+vote.numNay+vote.numPresent+vote.numNV)
                       if percentAye > .65 or percentNay < .35:
                           tr.points+=500 #if lopsided vote then vote with conscience so add points
                          
               
               tr.vote=vote
               #if tr.points > 0:
                   # try:
                   #                        print tr
                   #                    except Exception:
                   #                        pass
                       
               try:
                   tr.save()
               except Exception,ex:
                   print ex

def getVoteReport(session):
      for i,vote in enumerate(Vote.objects.filter(Q(bill__congress__number=session)|Q(amendment__bill__congress__number=session))):
          print i       
          trs = TempRepPoints.objects.filter(vote=vote).order_by('-points')
          if trs.count() > 5:
              trs = trs[0:5]
          
          try:
              vr = VoteReport.objects.filter(vote=vote)[0]
          except Exception:
              vr=VoteReport()
          vr.hasInd=False
          vr.hasContr=False
          vr.hasComm = False
          vr.hasOrgs = False
          vr.hasDiff=False
          vr.hasElec=False
          vr.hasStance=False
          vr.save()
          
          for tr in trs:
              
              voter = tr.rep
              if not vr.hasElec:
                  pr = PredElectionReport.objects.filter(vote=vote,predElection__rep=voter)
                  if pr.count() > 0:
                      vr.hasElec=True
                      vr.save()
              
              if not vr.hasDiff:
                  st = StatePVIReport.objects.filter(vote=vote,rep=voter)
                  if st.count() > 0:
                      vr.hasDiff=True
                      vr.save()
           
              if not vr.hasComm:
                  ccs = ChairCommitteeReport.objects.filter(vote=vote,rep=voter)
                  if ccs.count()>0:
                      vr.hasComm=True
                      vr.save()
             
              if not vr.hasInd:
                  naicsObjs = NAICSIndustryReport.objects.filter(vote=vote,rep=voter) 
                  if naicsObjs.count()>0:
                      vr.hasInd=True
                      vr.save()
              
              if not vr.hasContr:
                  contrObjs = RepContributionReport.objects.filter(vote=vote,rep=voter)
                  if contrObjs.count()>0:
                      vr.hasContr=True
                      vr.save()
              
              if not vr.hasStance and not vote.hasAmendment:
                  rcs = RepContributionReport.objects.filter(vote=vote,rep=voter)
                  sectors = list(set(rcs.values_list('bus__industry__sector',flat=True)))
                  for sector in sectors:
                     rc_buses = rcs.filter(bus__industry__sector=sector)
                     for bus in rc_buses:
                         amtCompFor=0
                         amtCompAgainst=0

                         for rc in rc_buses:
                              if rc.amtMoneyFor != None:
                                  amtCompFor += rc.amtMoneyFor

                              if rc.amtMoneyAgainst!=None:
                                  amtCompAgainst += rc.amtMoneyAgainst

                         if amtCompFor>0:
                              print 'HAS STANCE'
                              vr.hasStance=True
                              vr.save()
                              break
                         if amtCompAgainst>0:
                              print 'HAS STANCE'
                              vr.hasStance=True
                              vr.save()
                              break
              
             
if __name__ == '__main__':
   #findExpsTest()
   #assignPoints(111)
   #findAllExps(111)
   findAllExps(112)
   #assignPoints(111)
   #getVoteReport(111)
   #assignPoints(112)
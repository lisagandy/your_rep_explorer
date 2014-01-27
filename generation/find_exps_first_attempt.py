from ccu_gen_beta.models import *
from ccu_utilities import isOutlier,describeVote
from datetime import date,timedelta
from django.db.models import *
from xml.dom.minidom import Document
from django.core import serializers


partyPercentD = {}
adaScoresD = {}
industryPercentD = {}
contrD = {}

def biPartisanVoter(rep,doc,voterDoc):
    try:
        congress = rep.congress
    
        if congress.number not in partyPercentD:
            partyPercentD[congress.number] = [rw.withPartyScore for rw in RepWithParty.objects.filter(congress=congress)]
    
        isOut,typeOut = isOutlier(RepWithParty.objects.get(rep=rep).withPartyScore,partyPercentD[congress.number])
        if isOut and typeOut=='LOW':
            rp = RepWithParty.objects.get(rep=rep)
            bp = doc.createElement('bi-partisan-stats')
            bp.setAttribute('votes-bi-partisan','true')
            bp.setAttribute('party-percent-score','%s.00%%' % str(rp.withPartyScore))
            bp.setAttribute('source','http://projects.washingtonpost.com/congress/%d/senate/members/' % congress.number)
            index = partyPercentD[congress.number].index(rp.withPartyScore)
            bp.setAttribute('party-percent-rank','%s/100' % str(index+1))
            voterDoc.appendChild(bp)
        
    except Exception,ex:
        print ex
        assert 0
    return doc,voterDoc

def lookUpChoice(text,choice):
    for item in choice:
        if item[0] == text:
            return item[1]
    return None

def nextElectionRep(vote,rep,doc,voterDoc):
    pes = PredElection.objects.filter(rep=rep,date__lte=vote.dateVote).order_by('-date')
    
    pe = None
    if pes.count() > 0: pe= pes[0]
    else:
        return doc,voterDoc
    
    #if election is over a year away don't worry about it
    timeApart = pe.election.date - vote.dateVote
    if abs(timeApart.days) > 365:
        return doc,voterDoc
    
    pred = pe.pred
   
    found = False
    if rep.party=='R' and pred in ['SOLID_D','LIKE_D','LEAN_D','TU','LEAN_R']:
        found=True
      
    elif rep.party=='D' and pred in ['SOLID_R','LIKE_R','LEAN_R','TU','LEAN_D']:
        found=True
      
    elif pred in ['RS','RG','RM','PR','PS','PG','PM']:
        found=True
    
    if found:
        ne = doc.createElement('relevant-next-election')
        print lookUpChoice(pred,'PRED_ELEC_CHOICES')
        ne.setAttribute('current-race',lookUpChoice(pred,PRED_ELEC_CHOICES))
        ne.setAttribute('election-date',str(pe.election.date))
        ne.setAttribute('senate-class',str(pe.election.senateClass))
        ne.setAttribute('source','http://www.cookpolitical.com')
        ne.setAttribute('source-date',str(pe.date))
        voterDoc.appendChild(ne)
    
    return doc,voterDoc

def diffConstRep(vote,rep):
    repADAObjs = RepADA.objects.filter(rep=rep,year__lte=vote.dateVote.year).order_by('-year')
    if repADAObjs.count() > 0: repADAObj = repADAObjs[0]
    else: 
        #print 'WHY NO REP ADA %s %d' % (rep,vote.dateVote.year) 
        return
        #assert 0
    
    pviScores = StatePVI.objects.filter(state=rep.state,year__lte=vote.dateVote.year).order_by('-year')
    if pviScores.count() > 0: pviObj = pviScores[0]
    else: 
        #print 'WHY NO PVI %s %d' % (rep,vote.dateVote.year) 
        return
        #assert 0
    
    adaScore = repADAObj.adaScore
    
    if pviObj.demCook: pviScore = pviObj.scoreCook
    else: pviScore= 0 - pviObj.scoreCook
    
    #if typeOutADA is HIGH then that means super liberal, LOW means super conservative
    adaScores = [adaObj.adaScore for adaObj in RepADA.objects.filter(year=repADAObj.year,rep__senator=True)]
    adaScores.sort()
    isOutADA,typeOutADA = isOutlier(adaScore,adaScores)
    
    #same for cook pvi
    cookScores = []
    for pviObj in StatePVI.objects.filter(year=pviObj.year):
        if pviObj.demCook:cookScores.append(pviObj.scoreCook)
        else: cookScores.append(0-pviObj.scoreCook)
    cookScores.sort()
    isOutPVI,typeOutPVI = isOutlier(pviScore,cookScores)
   
    print ""
    if not typeOutADA or not typeOutPVI:
        return
    
    if typeOutADA.find('HIGH') > -1 and typeOutPVI.find('LOW') > -1:
        print 'rep %s more liberal than constituency %s' % (rep,rep.state)
    elif typeOutADA.find('LOW') > -1 and typeOutPVI.find('HIGH') > -1:
        print 'rep %s more conservative than constituency %s' % (rep,rep.state)
    

def findCommitteeChair(vote,voter,doc,voterDoc):
    
    if not vote.subtopics or vote.subtopics.all().count()==0:return doc,voterDoc
    voteTopics = []
    
    for st in vote.subtopics.all():
        if st.topic not in voteTopics:
            voteTopics.append(st.topic)
    
    relComms = Committee.objects.filter(topics__in=voteTopics,chair=voter)
    if len(relComms) > 0:
        for comm in relComms:
            comXML = doc.createElement('relevant-committee')
            comXML.setAttribute('name',comm.name)
            comXML.setAttribute('code',comm.code)
            comXML.setAttribute('chair','true')
            voterDoc.appendChild(comXML)
            
    
    relComms = Committee.objects.filter(topics__in=voteTopics,viceChair=voter)
    if len(relComms) > 0:
        for comm in relComms:
            comXML = doc.createElement('relevant-committee')
            comXML.setAttribute('name',comm.name)
            comXML.setAttribute('code',comm.code)
            comXML.setAttribute('vice-chair','true')
            voterDoc.appendChild(comXML)
           
    relComms = Committee.objects.filter(topics__in=voteTopics,rankingMember=voter)
    if len(relComms) > 0:
        for comm in relComms:
             comXML = doc.createElement('relevant-committee')
             comXML.setAttribute('name',comm.name)
             comXML.setAttribute('code',comm.code)
             comXML.setAttribute('ranking-member','true')
             voterDoc.appendChild(comXML)
             
    return doc,voterDoc

          

def findRelIndustries(vote,voter,doc,voterDoc,finalReport):
    if vote.subtopics.all().count() == 0:
        print 'NO SUBTOPICS FOR VOTE'
        return doc,voterDoc
    
    #utilize already existing org stances to limit which
    #industries we look at
    mlBusinessLimit = []
    if vote.bill.orgStances.all().count() > 0:
        mlBusinessLimit.extend([og.org.mlBusiness for og in vote.bill.orgStances.all()])
    
        #find maplight businesses associated to this topic
        mlBusinessST = list(MapLightBusiness.objects.filter(subtopics__in=vote.subtopics.all()))
        if len(mlBusinessLimit) > 0:
            mlBusinessST = set(mlBusinessST).intersection(set(mlBusinessLimit))
            mlBusinessST = list(mlBusinessST)
        
        if len(mlBusinessST) == 0: MapLightBusiness.objects.filter(subtopics__in=vote.subtopics.all())
    else:
        #print vote.subtopics.all()
        mlBusinessST = MapLightBusiness.objects.filter(subtopics__in=vote.subtopics.all())
    
    #get related industries for subtopics related to vote...
    #print voter.state
    #print mlBusinessST
    industries = list(set([nai.naicsIndustry for nai in NAICS_Locale.objects.filter(state=voter.state,naicsIndustry__mlBusinesses__in=mlBusinessST)]))
    
    for industry in industries:
        strLookup = str(industry) + '_' + str(vote.dateVote.year)
        if not strLookup in industryPercentD:
            lsAll = []
            for state in State.objects.all():
                objs = NAICS_Locale.objects.filter(naicsIndustry=industry,endYear__gte=vote.dateVote.year,state=state).order_by('-endYear')
                if len(objs) > 0:
                    lsAll.append(objs[0].percentage(vote.dateVote))
                else:

                    lsAll.append(0)
            
            industryPercentD[strLookup] = lsAll
        
        voterIndustry = NAICS_Locale.objects.filter(naicsIndustry=industry,state=voter.state,endYear__gte=vote.dateVote.year).order_by('-endYear')[0]
        percentEmps = voterIndustry.percentage(vote.dateVote)
        isOut,typeOut= isOutlier(percentEmps,industryPercentD[strLookup])
        if isOut and typeOut.find('HIGH') > -1:
            ri = doc.createElement('relevant-industry')
            finalReport.naicsLocales.add(industry)
            ri.setAttribute('name',industry.name)
            ri.setAttribute('naics-code',industry.code)
            ri.setAttribute('state',str(voter.state).title())
            #percentEmpsFormat = percentEmps * 100
            ri.setAttribute('percent-pop-emps','%.2f%%' % percentEmpsFormat)
            ri.setAttribute('source','http://lehd.did.census.gov/led/')
            ri.setAttribute('source-begin-year',str(voterIndustry.beginYear))
            ri.setAttribute('source-end-year',str(voterIndustry.endYear))
            lsNew = industryPercentD[strLookup]
            lsNew.reverse()
            rankIndex = lsNew.index(percentEmps)
            ri.setAttribute('rank-percent-pop-emps',"%s/50" % str(rankIndex+1))
            voterDoc.appendChild(ri)
    return doc,voterDoc
    
def findRelContrs(vote,voter,doc,voterDoc,finalReport):        
    mlBuses = []
    mlCite = []
    orgUsed = True
    
    if vote.bill.orgStances.all().count() > 0:
        mlBuses.extend([orgSt.org.mlBusiness for orgSt in vote.bill.orgStances.all()])
        #mlCite.extend([orgSt.wholeCite for orgSt in vote.bill.orgStances.all()])
        orgUsed= True
        #print 'Got business from organization stance'
    else:
        mlBuses = list(MapLightBusiness.objects.filter(subtopics__in=vote.subtopics.all()))
        #print 'Got business from automatic mapping'
    
    #make sure businesses are unique
    mlBuses = list(set(mlBuses))
    
    oldDate = vote.dateVote-timedelta(days=365)
    for i,bus in enumerate(mlBuses):
        if  RepContribution.objects.filter(rep=voter,dateContr__lte=vote.dateVote,dateContr__gte=oldDate,mlBusiness=bus).count() > 0:
            contrObjs = RepContribution.objects.filter(rep=voter,dateContr__lte=vote.dateVote,dateContr__gte=oldDate,mlBusiness=bus)
            totalAmt = contrObjs.aggregate(Sum('amountContr'))['amountContr__sum']
            
            lookupStr = bus.name + ':' + str(vote.dateVote) + ':' + str(oldDate)
            lsTotalAmt = []
            if lookupStr in contrD:
                lsTotalAmt = contrD[lookupStr]
            else:
                for rep in Rep.objects.filter(congress=vote.bill.congress.number,senator=True):
                    if RepContribution.objects.filter(rep=rep,dateContr__lte=vote.dateVote,dateContr__gte=oldDate,mlBusiness=bus).count() > 0:
                        contrObjs = RepContribution.objects.filter(rep=rep,dateContr__lte=vote.dateVote,dateContr__gte=oldDate,mlBusiness=bus)
                        totalAmt = contrObjs.aggregate(Sum('amountContr'))['amountContr__sum']
                        lsTotalAmt.append(totalAmt)
                    else:
                        lsTotalAmt.append(0)
                lsTotalAmt.sort()
                contrD[lookupStr] = lsTotalAmt
            
            isOut,typeOut = isOutlier(totalAmt,lsTotalAmt)
            if totalAmt > 40000 and isOut and typeOut.find('MILD HIGH') > -1:
                finalReport.mlBusinesses.append(bus)
                rc = doc.createElement('relevant-contribution')
                rc.setAttribute('business-type',bus.name)
                rc.setAttribute('business-code',bus.mlID)
                rc.setAttribute('totalAmt',str(totalAmt))
                index = (len(contrD[lookupStr]) - contrD[lookupStr].index(totalAmt)) + 1
                rc.setAttribute('contribution-rank','%s/100' % str(index))
                rc.setAttribute('contribution-end-date',str(vote.dateVote))
                rc.setAttribute('contribution-start-date',str(oldDate))
                if orgUsed:
                    rc.setAttribute('mapping-type','org-stance')
                    #print 'Got business from organization stance'
                else:
                    rc.setAttribute('mapping-type','automatic')
                    #print 'Got business from automatic mapping'
                voterDoc.appendChild(rc)
                #print ""
    return doc,voterDoc,finalReport
    
def createXMLVoter(vote,voter,anomVoters,doc):
    voterDoc = doc.createElement('voter')
    anomVoters.appendChild(voterDoc)
    infoDoc = doc.createElement('voter-info')
    infoDoc.setAttribute('lastname',voter.lastName)
    infoDoc.setAttribute('osid',voter.repID)
    infoDoc.setAttribute('gov-track-id',voter.repGovTrackID)
    infoDoc.setAttribute('firstname',voter.firstName)
    infoDoc.setAttribute('state',str(voter.state).title())
    if voter.party == 'R':
        infoDoc.setAttribute('party','Republican')
    elif voter.party == 'D':
        infoDoc.setAttribute('party','Democrat')
    else:
        infoDoc.setAttribute('party','Other')
    infoDoc.setAttribute('chamber','senate')
    voterDoc.appendChild(infoDoc)
    
    doc,voterDoc = biPartisanVoter(voter,doc,voterDoc)
    doc,voterDoc = nextElectionRep(vote,voter,doc,voterDoc)
    doc,voterDoc = findCommitteeChair(vote,voter,doc,voterDoc)
    doc,voterDoc,finalReport = findRelIndustries(vote,voter,doc,voterDoc,finalReport)
    doc,voterDoc,finalReport = findRelContrs(vote,voter,doc,voterDoc,finalReport)
    return voterDoc,doc,finalReport
        
def findExps(vote):
    
    try:
        avObj = AnomVoters.objects.get(vote=vote)
        #print avObj
    except Exception:
        #print "NO OBJ FOR %s " % vote
        return
    
    finalReport = FinalReport.objects.get_or_create(vote=vote)[0]
    demVoters = [dv.rep for dv in avObj.demVoters.all().order_by('rep__lastName')]
    repVoters = [rv.rep for rv in avObj.repVoters.all().order_by('rep__lastName')]
    print describeVote(vote)
    doc = Document()
    anomVoters = doc.createElement('anom-voters')
    doc.appendChild(anomVoters)
    for voter in demVoters:
        voterDoc,doc,finalReport = createXMLVoter(vote,voter,anomVoters,doc,finalReport)
              
    for voter in repVoters: 
        voterDoc,doc,finalReport = createXMLVoter(vote,voter,anomVoters,doc,finalReport)
    
    
    #print doc.toprettyxml()
    #assert 0
   #print ""


    
def findAllExps(session):
    for vote in Vote.objects.filter(active=True): 
        findExps(vote)
        
    
if __name__ == '__main__':
    findAllExps(111)
    findAllExps(112)
    
# Create your views here.
from django.http import HttpResponse
from your_rep_explorer.ccu_gen_beta.models import *
from django.template import Context, loader
from ccu_utilities import *
from JulianTime import convertDateTimeJul
import datetime
import simplejson
from django.db.models import Q

#ref_url_basic='http://www.ccu-dev.com/'
#ref_url='http://ragnarok.cs.northwestern.edu/ccu_media/'
ref_url_basic='http://127.0.0.1:8000'
ref_url=''
on_remote_server=False

def hasReport(vote):
    
    if PredElectionReport.objects.filter(vote=vote).count() > 0:
        return True
    if StatePVIReport.objects.filter(vote=vote).count() > 0:
        return True
    if ChairCommitteeReport.objects.filter(vote=vote).count() > 0:
        return True
    if NAICSIndustryReport.objects.filter(vote=vote).count() > 0:
        return True
    if  RepContributionReport.objects.filter(vote=vote).count() > 0:
        return True
    
    return False
    
def getAllSenators():
    lsTrack = []
    strSenators=""
    for rep in Rep.objects.filter(senator=True).order_by('lastName','congress__number'):
         obj1=None
         obj2=None
         if rep.party.lower().find('d') > -1:
             obj1 = AnomVoters.objects.filter(demVoters__rep=rep)
         else:
             obj2 = AnomVoters.objects.filter(demVoters__rep=rep)
         
         if (obj1!=None and obj1.count() == 0) or (obj2 and obj2.count() == 0):
             continue
          
         if rep.repID not in lsTrack:
             strSenators = strSenators + ("%s:%s*" % (rep.repID,rep.officialName()))
             lsTrack.append(rep.repID)
    return strSenators         

def getSenatorsCongress(congress):
    lsTrack=[]
    strSenators=""

    for rep in Rep.objects.filter(senator=True,congress__number=congress).order_by('lastName'):
       obj1 = None
       obj2 = None
       if rep.party.lower().find('d') > -1:
             obj1 = AnomVoters.objects.filter(demVoters__rep=rep)
       else:
             obj2 = AnomVoters.objects.filter(demVoters__rep=rep)
         
       if (obj1!=None and obj1.count() == 0) or (obj2 and obj2.count() == 0):
             continue
       if rep.repID not in lsTrack:
           strSenators = strSenators + ("%s:%s*" % (rep.repID,rep.officialName()))
           lsTrack.append(rep.repID)
        
        
    
    return strSenators

def getSenatorsDate(date1,date2):
        lsTrack=[]
        strSenators=""
        
        testObjs = AnomVoters.objects.filter(vote__dateVote__gte=date1,vote__dateVote__lte=date2)
        if testObjs.count() == 0:
            return ""
        
        for rep in Rep.objects.filter(senator=True).order_by('lastName'):
           obj1 = None
           obj2 = None
           if rep.party.lower().find('d') > -1:    
               obj1 = AnomVoters.objects.filter(vote__dateVote__gte=date1,vote__dateVote__lte=date2,demVoters__rep=rep)
           else:
               obj2 = AnomVoters.objects.filter(vote__dateVote__gte=date1,vote__dateVote__lte=date2,repVoters__rep=rep)
           
           if (obj1!=None and obj1.count() == 0) or (obj2 and obj2.count() == 0):
                        continue
           if rep.repID not in lsTrack:
               strSenators = strSenators + ("%s:%s*" % (rep.repID,rep.officialName()))
               lsTrack.append(rep.repID)

        return strSenators
           
def getSenatorsTopic(topicID):
    strSenators=""
    lsTrack=[]
    for rep in Rep.objects.filter(senator=True).order_by('lastName','congress__number'):
         obj1 = None
         obj2 = None
         obj3 = None
         obj4 = None
         if rep.party.lower().find('d') > -1:  
             obj1 = AnomVoters.objects.filter(demVoters__rep=rep,vote__bill__subtopics__topic__code=topicID)
             obj2 = AnomVoters.objects.filter(demVoters__rep=rep,vote__amendment__subtopics__topic__code=topicID)
         else:
             obj3 = AnomVoters.objects.filter(repVoters__rep=rep,vote__bill__subtopics__topic__code=topicID)
             obj4 = AnomVoters.objects.filter(repVoters__rep=rep,vote__amendment__subtopics__topic__code=topicID)
         
         if (obj1!=None and obj1.count() == 0 and obj2.count() == 0) or (obj3!=None and obj3.count() == 0 and obj4.count() == 0):
             continue
          
         if rep.repID not in lsTrack:
             strSenators = strSenators + ("%s:%s*" % (rep.repID,rep.officialName()))
             lsTrack.append(rep.repID)
    return strSenators

def getSenatorsSubtopic(subtopicID):
    strSenators=""
    lsTrack=[]
    for rep in Rep.objects.filter(senator=True).order_by('lastName','congress__number'):
        obj1 = None
        obj2 = None
        obj3 = None
        obj4 = None
        if rep.party.lower().find('d') > -1:  
            obj1 = AnomVoters.objects.filter(demVoters__rep=rep,vote__bill__subtopics__code=subtopicID)
            obj2 = AnomVoters.objects.filter(demVoters__rep=rep,vote__amendment__subtopics__code=subtopicID)
        else:    
            obj3 = AnomVoters.objects.filter(repVoters__rep=rep,vote__bill__subtopics__code=subtopicID)
            obj4 = AnomVoters.objects.filter(repVoters__rep=rep,vote__amendment__subtopics__code=subtopicID)
            
        if (obj1!=None and obj1.count() == 0 and obj2.count() == 0) or (obj3!=None and obj3.count() == 0 and obj4.count() == 0):
                 continue

        if rep.repID not in lsTrack:
                strSenators = strSenators + ("%s:%s*" % (rep.repID,rep.officialName()))
                lsTrack.append(rep.repID)
    return strSenators

def getSenatorsDateTopic(date1,date2,topicID):
        strSenators=""
        lsTrack=[]   
        for rep in Rep.objects.filter(senator=True).order_by('lastName'):
           obj1 = None
           obj2 = None
           obj3 = None
           obj4 = None
           
           if rep.party.lower().find('d') > -1:
               obj1 = AnomVoters.objects.filter(vote__dateVote__gte=date1,vote__dateVote__lte=date2,demVoters__rep=rep,vote__bill__subtopics__topic__code=topicID)
               obj2 = AnomVoters.objects.filter(vote__dateVote__gte=date1,vote__dateVote__lte=date2,demVoters__rep=rep,vote__amendment__subtopics__topic__code=topicID)
           else:
               obj3 = AnomVoters.objects.filter(vote__dateVote__gte=date1,vote__dateVote__lte=date2,repVoters__rep=rep,vote__bill__subtopics__topic__code=topicID)
               obj4 = AnomVoters.objects.filter(vote__dateVote__gte=date1,vote__dateVote__lte=date2,repVoters__rep=rep,vote__amendment__subtopics__topic__code=topicID)    


           if (obj1!=None and obj1.count() == 0 and obj2.count() == 0) or (obj3!=None and obj3.count() == 0 and obj4.count() == 0):
                        continue
           
           if rep.repID not in lsTrack:
               strSenators = strSenators + ("%s:%s*" % (rep.repID,rep.officialName()))
               lsTrack.append(rep.repID)

        return strSenators

def getSenatorsDateSubtopic(date1,date2,subtopicID):
    strSenators=""
    lsTrack=[]   
    for rep in Rep.objects.filter(senator=True).order_by('lastName'):
       obj1 = None
       obj2 = None
       obj3 = None
       obj4 = None
       if rep.party.lower().find('d') > -1: 
           obj1 = AnomVoters.objects.filter(vote__dateVote__gte=date1,vote__dateVote__lte=date2,demVoters__rep=rep,vote__bill__subtopics__code=subtopicID)
           obj2 = AnomVoters.objects.filter(vote__dateVote__gte=date1,vote__dateVote__lte=date2,demVoters__rep=rep,vote__amendment__subtopics__code=subtopicID)
       else:
           obj3 = AnomVoters.objects.filter(vote__dateVote__gte=date1,vote__dateVote__lte=date2,repVoters__rep=rep,vote__bill__subtopics__code=subtopicID)
           obj4 = AnomVoters.objects.filter(vote__dateVote__gte=date1,vote__dateVote__lte=date2,repVoters__rep=rep,vote__amendment__subtopics__code=subtopicID)    


       if (obj1!=None and obj1.count() == 0 and obj2.count() == 0) or (obj3!=None and obj3.count() == 0 and obj4.count() == 0):
           continue
       
       if rep.repID not in lsTrack:
           strSenators = strSenators + ("%s:%s*" % (rep.repID,rep.officialName()))
           lsTrack.append(rep.repID)

    return strSenators
    
def getSenatorsCongressTopic(congress,topicID):
    strSenators=""
    lsTrack=[]   
    for rep in Rep.objects.filter(senator=True,congress__number=congress).order_by('lastName'):
       obj1 = None
       obj2 = None
       obj3 = None
       obj4 = None
       if rep.party.lower().find('d') > -1: 
           obj1 = AnomVoters.objects.filter(demVoters__rep=rep,vote__bill__subtopics__topic__code=topicID)
           obj2 = AnomVoters.objects.filter(demVoters__rep=rep,vote__amendment__subtopics__topic__code=topicID)
       else:
           obj3 = AnomVoters.objects.filter(repVoters__rep=rep,vote__bill__subtopics__topic__code=topicID)
           obj4 = AnomVoters.objects.filter(repVoters__rep=rep,vote__amendment__subtopics__topic__code=topicID)    


       if (obj1!=None and obj1.count() == 0 and obj2.count() == 0) or (obj3!=None and obj3.count() == 0 and obj4.count() == 0):
            continue
       
       if rep.repID not in lsTrack:
           strSenators = strSenators + ("%s:%s*" % (rep.repID,rep.officialName()))
           lsTrack.append(rep.repID)
    
    return strSenators
    
def getSenatorsCongressSubtopic(congress,subtopicID):
    strSenators=""
    lsTrack=[]   
    for rep in Rep.objects.filter(senator=True,congress__number=congress).order_by('lastName'):
       obj1 = None
       obj2 = None
       obj3 = None
       obj4 = None
       if rep.party.lower().find('d') > -1:
           obj1 = AnomVoters.objects.filter(vote__bill__congress=congress,demVoters__rep=rep,vote__bill__subtopics__code=subtopicID)
           obj2 = AnomVoters.objects.filter(vote__bill__congress=congress,demVoters__rep=rep,vote__amendment__subtopics__code=subtopicID)
       else:
           obj3 = AnomVoters.objects.filter(vote__bill__congress=congress,repVoters__rep=rep,vote__bill__subtopics__code=subtopicID)
           obj4 = AnomVoters.objects.filter(vote__bill__congress=congress,repVoters__rep=rep,vote__amendment__subtopics__code=subtopicID)    


       if (obj1!=None and obj1.count() == 0 and obj2.count() == 0) or (obj3!=None and obj3.count() == 0 and obj4.count() == 0):
            continue
       
       if rep.repID not in lsTrack:
           strSenators = strSenators + ("%s:%s*" % (rep.repID,rep.officialName()))
           lsTrack.append(rep.repID)

    return strSenators

def getSubtopicCongress(congress,topicID):
    strSubTopics = ""
    for subtopic in JonesSubTopic.objects.filter(topic__code=topicID).order_by('name'):
        obj1 = AnomVoters.objects.filter(vote__bill__congress__number=congress,vote__bill__subtopics=subtopic)
        obj2 = AnomVoters.objects.filter(vote__bill__congress__number=congress,vote__amendment__subtopics=subtopic)
        if obj1.count() > 0 or obj2.count() > 0:
            strSubTopics = strSubTopics + ("%s:%s*" % (subtopic.code,subtopic.name))
    return strSubTopics
    
def getSubtopicDate(date1,date2,topicID):
    strSubTopics = ""
    for subtopic in JonesSubTopic.objects.filter(topic__code=topicID).order_by('name'):
        obj1 = AnomVoters.objects.filter(vote__dateVote__gte=date1,vote__dateVote__lte=date2,vote__bill__subtopics=subtopic)
        obj2 = AnomVoters.objects.filter(vote__dateVote__gte=date1,vote__dateVote__lte=date2,vote__amendment__subtopics=subtopic)
        if obj1.count() > 0 or obj2.count() > 0:
            strSubTopics = strSubTopics + ("%s:%s*" % (subtopic.code,subtopic.name))
    return strSubTopics

def getAllSubtopics(topicID): 
    strSubTopics = ""   
    for subtopic in JonesSubTopic.objects.filter(topic__code=topicID).order_by('name'): 
       obj1 = AnomVoters.objects.filter(vote__bill__subtopics=subtopic)
       obj2 = AnomVoters.objects.filter(vote__amendment__subtopics=subtopic)
       if obj1.count() > 0 or obj2.count() > 0:
             strSubTopics = strSubTopics + ("%s:%s*" % (subtopic.code,subtopic.name)) 
    return strSubTopics

def getTopicCongress(congress):
        strTopics = ""
        for topic in JonesTopic.objects.all().order_by('name'):
            obj1 = AnomVoters.objects.filter(vote__bill__congress__number=congress,vote__bill__subtopics__topic=topic)
            obj2 = AnomVoters.objects.filter(vote__bill__congress__number=congress,vote__amendment__subtopics__topic=topic)
            if obj1.count() > 0 or obj2.count() > 0:
                strTopics = strTopics + ("%s:%s*" % (topic.code,topic.name))
        return strTopics

def getTopicDate(date1,date2):
        strTopics = ""
        for topic in JonesTopic.objects.all().order_by('name'):
            obj1 = AnomVoters.objects.filter(vote__dateVote__gte=date1,vote__dateVote__lte=date2,vote__bill__subtopics__topic=topic)
            obj2 = AnomVoters.objects.filter(vote__dateVote__gte=date1,vote__dateVote__lte=date2,vote__amendment__subtopics__topic=topic)
            if obj1.count() > 0 or obj2.count() > 0:
                strTopics = strTopics + ("%s:%s*" % (topic.code,topic.name))
        return strTopics

def getAllTopics(): 
        strTopics = ""   
        for topic in JonesTopic.objects.all().order_by('name'): 
           obj1 = AnomVoters.objects.filter(vote__bill__subtopics__topic=topic)
           obj2 = AnomVoters.objects.filter(vote__amendment__subtopics__topic=topic)
           if obj1.count() > 0 or obj2.count() > 0:
                 strTopics = strTopics + ("%s:%s*" % (topic.code,topic.name)) 
        return strTopics
        
def pop_select_boxes_subtopic(request,date,topicID,subtopicID):
    congress=None
    strSenators=""
    date1 = None
    date2 = None
    if subtopicID=="all":
        if date=="all":
            strSenators = getSenatorsTopic(topicID)
        elif date.find('*') > -1:
            date1 = createDate5(date.split('*')[0])  
            date2 = createDate5(date.split('*')[1])
            strSenators = getSenatorsDateTopic(date1,date2,topicID)
        else:
            if date.lower().find('past') > -1 or date=='112':
                    congress=112
            else:
                    congress=111
            strSenators = getSenatorsCongressTopic(congress,topicID) 
    else:
        if date=="all":
            strSenators = getSenatorsSubtopic(subtopicID)
        elif date.find('*') > -1:
            date1 = createDate5(date.split('*')[0])  
            date2 = createDate5(date.split('*')[1])
            strSenators = getSenatorsDateSubtopic(date1,date2,topicID)
        else:
            if date.lower().find('past') > -1 or date=='112':
                    congress=112
            else:
                    congress=111
            strSenators = getSenatorsCongressSubtopic(congress,subtopicID)
    
    dRet = {}
    dRet['senators'] = strSenators[0:-1]
    return HttpResponse(simplejson.dumps(dRet), mimetype='application/json')

def pop_select_boxes_state(request,date,state):
    
    if state.lower().find('all') > -1:
        senators = Rep.objects.filter(senator=True).order_by('lastName')
    else:
        senators = Rep.objects.filter(senator=True,state__name=state).order_by('lastName')
        
    if date=="112":
        senators = senators.filter(congress__number=112)
    elif date=="111":
        senators =  senators.filter(congress__number=111)
    
    lsTrack = []
    strSenators = ""
    for rep in senators:    
        if rep.repID not in lsTrack:
            strSenators = strSenators + ("%s:%s*" % (rep.repID,rep.officialName()))
            lsTrack.append(rep.repID)
    
    dRet={}
    dRet['senators'] = strSenators[0:-1]
    return HttpResponse(simplejson.dumps(dRet), mimetype='application/json')
    
    
           
def pop_select_boxes_topic(request,date,topicID):
    #topic narrows down senators
    #topic narrows down subtopics
    strSenators = ""
    strTopics = ""
    strSubtopics = ""
    lsTrack = []
    congress=None
    date1 = None
    date2 = None
    
    if date=='all':
        if topicID != "all":
            topicID=int(topicID)
            strSenators = getSenatorsTopic(topicID)
        else:
            strSenators = getAllSenators()
    elif date.find('*') > -1:
        date1 = createDate5(date.split('*')[0])  
        date2 = createDate5(date.split('*')[1])
        if topicID=="all":
            strSenators = getSenatorsDate(date1,date2)    
        else:
            strSenators = getSenatorsDateTopic(date1,date2,topicID)
    else:
        if date.lower().find('past') > -1 or date=='112':
                congress=112
        else:
                congress=111
        
        if topicID=="all":
            strSenators = getSenatorsCongress(congress)
        else:
            topicID = int(topicID)
            strSenators = getSenatorsCongressTopic(congress,topicID)
            
    
    strSubTopics = ""
    if topicID!="all":
        if congress:
            strSubTopics = getSubtopicCongress(congress,topicID)
        elif date1:
            strSubTopics = getSubtopicDate(date1,date2,topicID)
        else: #all dates
            strSubTopics = getAllSubtopics(topicID)
               
    dRet = {}
    dRet['senators'] = strSenators[0:-1]
    if strSubTopics!="":
        dRet['subtopics'] = strSubTopics[0:-1]
    else:
        dRet['subtopics'] = strSubTopics
    return HttpResponse(simplejson.dumps(dRet), mimetype='application/json')

def pop_select_boxes(request,date):

   strSenators = ""
   strTopics = ""
   lsTrack = []
   congress=None
   date1=None
   date2=None
   
   #return HttpResponse(simplejson.dumps(date), mimetype='application/json')
   if date=='all':
         strSenators = getAllSenators()
   elif date.find('*') > -1:
         date1 = createDate5(date.split('*')[0])  
         date2 = createDate5(date.split('*')[1])
         #strSenators=""
         strSenators = getSenatorsDate(date1,date2)   
             
   else:         
         if date.lower().find('past') > -1 or date=='112':
                  congress=112
         else:
                  congress=111 
         strSenators  = getSenatorsCongress(congress)
            
   if congress==111 or congress==112:
             strTopics = getTopicCongress(congress)
   elif date1:
             strTopics = getTopicDate(date1,date2)
   else:
             strTopics = getAllTopics()
             
   retD = {}
   retD['senators'] = strSenators[0:-1]
   retD['topics'] = strTopics[0:-1]
   json = simplejson.dumps(retD)
      
   return HttpResponse(json, mimetype='application/json')


def choose_votes(request):
       global ref_url
       dRet = {}
       lsTimes=[]
       lsTimes.append(('All Votes','all'))
       lsTimes.append(('112 Congress','112'))
       lsTimes.append(('111 Congress','111'))
       lsTimes.append(('Choose dates','choose'))
    
       lsSenator = [('All Senators','all')]
       lsTrack = []
       for rep in Rep.objects.filter(senator=True).order_by('lastName','congress__number'):
               if not AnomVoters.objects.filter(demVoters=rep) and not AnomVoters.objects.filter(repVoters=rep):
                   continue
               if not rep.repID in lsTrack:
                   lsSenator.append([rep.officialName(),rep.repID])
                   lsTrack.append(rep.repID)
       
       #strSenators = getAllSenators()           
       lsTopics = []
       
       for topic in JonesTopic.objects.all().order_by('name'):
           votes1 = Vote.objects.filter(amendment__subtopics__topic=topic)
           votes2 = Vote.objects.filter(bill__subtopics__topic=topic)
           if votes1.count() > 0 or votes2.count() > 0:
               lsTopics.append(topic)
      
       t = loader.get_template('votes/index_choose_votes.html')
       dRet['time_choices'] = lsTimes
       dRet['lsSenators'] = lsSenator
       dRet['lsTopics'] = lsTopics
       dRet['refURL'] = ref_url
       c = Context(dRet)
       return HttpResponse(t.render(c))

def getAllBusinesses(indID):
     strBuses = ""
     for bus in MapLightBusiness.objects.filter(industry__code=indID).order_by('name'):
         if bus.name.lower()=='other':
                continue
         rc1 = RepContributionReport.objects.filter(mlBusiness=bus)
         if rc1.count() > 0:
             strBuses = strBuses + ("%s:%s*" % (bus.mlID,bus.name))
     return strBuses



def getAllIndustries(sectorID):
      strInds = ""
      for industry in MapLightIndustry.objects.filter(sector__code=sectorID).order_by('name'):
          if industry.name.lower()=='other':
                 continue
          rc1 = RepContributionReport.objects.filter(mlBusiness__industry=industry)
          if rc1.count() > 0:
              strInds = strInds + ("%s:%s*" % (industry.code,industry.name))
      return strInds

def getAllSectors():
       strSectors = ""
       for sector in MapLightSector.objects.all().order_by('name'):
           if sector.name.lower()=='other':
                  continue
           rc1 = RepContributionReport.objects.filter(mlBusiness__industry__sector=sector)
           if rc1.count() > 0:
               strSectors = strSectors + ("%s:%s*" % (sector.code,sector.name))
       return strSectors

def getBusinessDate(indID,date1,date2):
   strBuses = ""
   for bus in MapLightBusiness.objects.filter(industry__code=indID).order_by('name'):
       if bus.name.lower()=='other':
             continue
       rc1 = RepContributionReport.objects.filter(vote__dateVote__gte=date1,vote__dateVote__lte=date2,mlBusiness=bus)
       if rc1.count() > 0:
               strBuses = strBuses + ("%s:%s*" % (bus.mlID,bus.name))
   return strBuses



def getBusinessCongress(congress,indID):
     strBuses = ""
     for bus in MapLightBusiness.objects.filter(business__industry__code=indID).order_by('name'):
         if bus.name.lower()=='other':
             continue
         rc1 = RepContributionReport.objects.filter(vote__bill__congress=congress,mlBusiness=bus)
         if rc1.count() > 0:
             strBuses = strBuses + ("%s:%s*" % (bus.mlID,bus.name))
     return strInds

def getIndustryDate(sectorID,date1,date2):
    strInds = ""
    for industry in MapLightIndustry.objects.filter(sector__code=sectorID).order_by('name'):
        if industry.name.lower()=='other':
              continue
        rc1 = RepContributionReport.objects.filter(vote__dateVote__gte=date1,vote__dateVote__lte=date2,mlBusiness__industry=industry)
        if rc1.count() > 0:
                strInds = strInds + ("%s:%s*" % (industry.code,industry.name))
    return strInds

def getIndustryCongress(congress,sectorID):
  strInds = ""
  for industry in MapLightIndustry.objects.filter(sector__code=sectorID).order_by('name'):
      if industry.name.lower()=='other':
          continue
      rc1 = RepContributionReport.objects.filter(vote__bill__congress=congress,mlBusiness__industry=industry)
      if rc1.count() > 0:
          strInds = strInds + ("%s:%s*" % (industry.code,industry.name))
  return strInds

def getSectorDate(date1,date2):
       strSectors = ""
       for sector in MapLightSector.objects.all().order_by('name'):
           if sector.name.lower()=='other':
               continue
           rc1 = RepContributionReport.objects.filter(vote__dateVote__gte=date1,vote__dateVote__lte=date2,mlBusiness__industry__sector=sector)
           if rc1.count() > 0:
               strSectors = strSectors + ("%s:%s*" % (sector.code,sector.name))
       return strSectors


def getSectorCongress(congress):
     strSectors = ""
     for sector in MapLightSector.objects.all().order_by('name'):
         if sector.name.lower()=='other':
             continue
         rc1 = RepContributionReport.objects.filter(vote__bill__congress=congress,mlBusiness__industry__sector=sector)
         if rc1.count() > 0:
             strSectors = strSectors + ("%s:%s*" % (sector.code,sector.name))
     return strSectors

def getSectorCongress(congress):
   strSectors = ""
   for sector in MapLightSector.objects.all().order_by('name'):
       if sector.name.lower()=='other':
           continue
       rc1 = RepContributionReport.objects.filter(vote__bill__congress=congress,mlBusiness__industry__sector=sector)
       if rc1.count() > 0:
           strSectors = strSectors + ("%s:%s*" % (sector.code,sector.name))
   return strSectors

def pop_select_boxes_business(request,date,indID):
          '''HERE NOW'''
          strBuses = ""
          congress=None
          date1=None
          date2=None
          indID=int(indID)

          if congress==111 or congress==112:
              strBuses = getBusinessCongress(congress,indID)
          elif date.find('*') > -1:
                date1 = createDate5(date.split('*')[0])  
                date2 = createDate5(date.split('*')[1])
                strBuses = getBusinessDate(indID,date1,date2)
          else:
              strBuses = getAllBusinesses(indID) 

          #print 'got industries'
          retD = {}
          retD['businesses'] = strBuses[0:-1]
          json = simplejson.dumps(retD)

          return HttpResponse(json, mimetype='application/json')

def pop_select_boxes_industry(request,date,sectorID):
      '''HERE NOW'''
      strSenators = ""
      strSectors = ""
      congress=None
      date1=None
      date2=None
      sectorID=int(sectorID)
          
      if congress==111 or congress==112:
          strIndustries = getIndustryCongress(congress,sectorID)
      elif date.find('*') > -1:
          date1 = createDate5(date.split('*')[0])  
          date2 = createDate5(date.split('*')[1])
          strIndustries = getIndustryDate(sectorID,date1,date2)       
      else:
          strIndustries = getAllIndustries(sectorID) 

      #print 'got industries'
      retD = {}
      #retD['senators'] = strSenators[0:-1]
      retD['industries'] = strIndustries[0:-1]
      json = simplejson.dumps(retD)

      return HttpResponse(json, mimetype='application/json')


def pop_select_boxes_sector(request,date):

      strSenators = ""
      strSectors = ""
      congress=None
      date1=None
      date2=None

      if congress==111 or congress==112:
          strSectors = getSectorCongress(congress)
      elif date.find('*') > -1:
               date1 = createDate5(date.split('*')[0])  
               date2 = createDate5(date.split('*')[1])
               strSectors = getSectorDate(date1,date2)
      else:
          strSectors = getAllSectors()

      retD = {}
      #retD['senators'] = strSenators[0:-1]
      retD['sectors'] = strSectors[0:-1]
      json = simplejson.dumps(retD)

      return HttpResponse(json, mimetype='application/json')


def choose_votes2(request):
      global ref_url
      dRet = {}
      lsTimes=[]
      lsTimes.append(('All Votes','all'))
      lsTimes.append(('112 Congress','112'))
      lsTimes.append(('111 Congress','111'))
      lsTimes.append(('Choose dates','choose'))

      lsSenator = [('All Senators','all')]
      lsTrack = []
      for rep in Rep.objects.filter(senator=True).order_by('lastName','congress__number'):
              if not AnomVoters.objects.filter(demVoters=rep) and not AnomVoters.objects.filter(repVoters=rep):
                  continue
              
              if not rep.repID in lsTrack:
                  lsSenator.append([rep.officialName(),rep.repID])
                  lsTrack.append(rep.repID)

      #strSenators = getAllSenators()           
      lsSectors = []

      for sector in MapLightSector.objects.all().order_by('name'):
          if sector.name.lower()=='other':
                continue
          rc = RepContributionReport.objects.filter(mlBusiness__industry__sector=sector)
          if rc.count() > 0:
              lsSectors.append(sector)

      t = loader.get_template('votes/index_choose_votes2.html')
      dRet['time_choices'] = lsTimes
      dRet['lsSenators'] = lsSenator
      dRet['lsSectors'] = lsSectors
      dRet['refURL'] = ref_url

      c = Context(dRet)
      return HttpResponse(t.render(c))
      
def choose_votes_senator(request):
        global ref_url
        dRet = {}
        lsTimes=[]
        lsTimes.append(('112 & 111 Congress','all'))
        lsTimes.append(('112 Congress','112'))
        lsTimes.append(('111 Congress','111'))

        lsStates = ['All states']
        for state in State.objects.all().order_by('name'):
            if Rep.objects.filter(state=state).count() > 0:
                lsStates.append(state.name)

        t = loader.get_template('votes/index_choose_votes_senator.html')
        dRet['time_choices'] = lsTimes
        dRet['lsStates'] = lsStates
        dRet['refURL'] = ref_url

        c = Context(dRet)
        return HttpResponse(t.render(c))

def all_votes_xml(request,session):
    return load_votes(request,session,xml=True)

def all_votes112_senate(request):
    return load_votes(request,112,senate=True)
   
def all_votes111_senate(request):
    return load_votes(request,111,senate=True) 

def all_votes112_house(request):
    return load_votes(request,112,senate=False)

def all_votes111_house(request):
    return load_votes(request,111,senate=False)           

def load_votes(request,session,senate=True,xml=False):
    start = datetime.datetime.now()
    global on_remote_server
    
    if senate:
        votes = Vote.objects.filter(bill__congress=session,senateVote=True).order_by('-dateVote','-number')
    else:
        votes = Vote.objects.filter(bill__congress=session,senateVote=False).order_by('-dateVote','-number')
    
    lsDescribe=[]
    lsAllInf=[]
    lsCloseVote=[]
    for vote in votes:
        hasPoints=False
        trs = TempRepPoints.objects.filter(vote=vote)
        for tr in trs:
            # print tr.points
            if tr.points > 0:
                hasPoints=True
                break
                
        if not hasPoints:
            continue

        
        lsTypeInf=[]
        
        html_descript = vote.htmlDescript
        if on_remote_server:
           html_descript = html_descript.replace('127.0.0.1:8000','www.ccu-dev.com')
        
        lsDescribe.append(html_descript)
        voteReport = VoteReport.objects.filter(vote=vote)[0]    
        hasPVI=False
        
        if abs(vote.percentNeeded - vote.percentGotten)*100 <=7 or abs(vote.percentGotten-vote.percentNeeded)*100 <= 7:
            lsCloseVote.append(True)
        else:
            lsCloseVote.append(False)
        
        if voteReport.hasDiff:
            lsTypeInf.append('statediff')

        if voteReport.hasContr:
            lsTypeInf.append('contribution')

        if voteReport.hasStance:
            lsTypeInf.append('company')

        if voteReport.hasInd:
            lsTypeInf.append('industry')

        if voteReport.hasElec:
            lsTypeInf.append('election')
        
        if voteReport.hasComm:
            lsTypeInf.append('committee')

        lsAllInf.append(lsTypeInf)


    if xml:
        t = loader.get_template('votes/all_votes.xml')
        c = Context({'refURL':ref_url_basic,'votes':zip(votes,lsContr,lsInd,lsOther,lsComm,lsPVI)})
        return HttpResponse(t.render(c), mimetype='application/xml')
    else:
        t = loader.get_template('votes/index.html')
        c = Context({'senate':senate,'refURLBasic':ref_url_basic,'refURL':ref_url,'session':session,'votes':zip(votes,lsDescribe,lsAllInf,lsCloseVote)})
        end = datetime.datetime.now()
        diff = end-start
        print diff
        return HttpResponse(t.render(c))
        

def load_votes_contr(request,date,sectorID,indID,busID,senatorIDS):
    avs=None
    if date=='all':
        avs = AnomVoters.objects.all()
    elif date.find('*') > -1:
        date1 = createDate5(date.split('*')[0])  
        date2 = createDate5(date.split('*')[1])
        avs = AnomVoters.objects.filter(vote__dateVote__gte=date1,vote__dateVote__lte=date2)
    else:
        avs = AnomVoters.objects.filter(vote__bill__congress__number=int(date))
    
    avs = avs.order_by('-vote__dateVote','-vote__number')    
    lsTrack = []
    dHTML = {}
    i=0
    newAVS = []
    lsSenatorCodes = [code for code in senatorIDS.split('*') if code.strip()!=""]
    typeDescript=None
    if busID != 'none' and busID!='all':
        typeDescript="contrBus"
    elif indID!='none' and indID!='all':
        typeDescript="contrInd"
    elif sectorID!='none':
        typeDescript="contrSector"
            
    for av in avs:
        rcs = RepContributionReport.objects.filter(vote=av.vote)
        if busID != 'none' and busID!='all':
            rcs = rcs.filter(mlBusiness__mlID=busID)
            
            
        elif indID!='none' and indID!='all':
            rcs =  rcs.filter(mlBusiness__industry__code=indID)   
            
        elif sectorID!='none' and sectorID!='all':
            rcs =  rcs.filter(mlBusiness__industry__sector__code=sectorID)   
            descriptType="contrSector"
        
        if senatorIDS!='none' and senatorIDS!='all':
            rcs = rcs.filter(rep__repID__in=lsSenatorCodes)        
        if rcs.count() > 0:
            newAVS.append(av)    

    i = 0
    dHTML = {}
    for av in newAVS:
        if hasReport(av.vote):
            dHTML[i] = describeVoteHTML(av.vote,typeDescript=typeDescript)
            i=i+1
    
    dRet={}
    dRet['html_descript']=dHTML
                    
    return HttpResponse(simplejson.dumps(dRet), mimetype='application/json')

def load_votes_senator(request,date,stateName,senatorIDS):
        avs=None
        if date=='all':
            avs = AnomVoters.objects.all()
        else:
            avs = AnomVoters.objects.filter(vote__bill__congress__number=int(date))

        avs = avs.order_by('-vote__dateVote','-vote__number')    
        lsTrack = []
        dHTML = {}
        
        #print avs.all()
        
        if senatorIDS!='none' and senatorIDS!='all':
            lsSenatorCodes = [code for code in senatorIDS.split('*') if code.strip()!=""]
            avs1 = avs.filter(demVoters__rep__repID__in=lsSenatorCodes)
            avs2 = avs.filter(repVoters__rep__repID__in=lsSenatorCodes)   
        else:
            #print stateName
            #print avs
            avs1 = avs.filter(demVoters__rep__state__name__iexact=stateName.lower())
            avs2 = avs.filter(repVoters__rep__state__name__iexact=stateName.lower())
            #print avs1
            #print avs2
            
        avs1 = list(avs1)
        avs2 = list(avs2)   
        avs1.extend(avs2)
        avs = avs1
                     
        i = 0
        dHTML = {}
        if avs:
            for av in avs:
                if hasReport(av.vote):
                    dHTML[i] = av.vote.htmlDescript
                    i=i+1

        dRet={}
        dRet['html_descript']=dHTML

        return HttpResponse(simplejson.dumps(dRet), mimetype='application/json')

def load_votes_topic(request,date,topicID,subtopicID,senatorIDS):
        try:
            if topicID!='all' and topicID!='none':
                topicID=int(topicID)
        except Exception:
            pass
        
        try:
            if subtopicID!='all' and subtopicID!='none':
                subtopicID=int(subtopicID)
        except Exception:
            pass
            
        avs = None
        if date=='all':
            avs = AnomVoters.objects.all()
            print "AVS IN ALL"
            print avs.count()
            
        elif date.find('*') > -1:
            date1 = createDate5(date.split('*')[0])  
            date2 = createDate5(date.split('*')[1])
            avs = AnomVoters.objects.filter(vote__dateVote__gte=date1,vote__dateVote__lte=date2)
        else:
            avs = AnomVoters.objects.filter(vote__bill__congress__number=int(date))
            
        avs = avs.order_by('-vote__dateVote','-vote__number')
        
        if senatorIDS!='none' and senatorIDS!='all':
            lsSenatorCodes = [code for code in senatorIDS.split('*') if code.strip()!=""]
            if not avs:
                avs = AnomVoters.objects.filter(Q(demVoters__rep__repID__in=lsSenatorCodes)|Q(repVoters__rep__repID__in=lsSenatorCodes))
            else:
                print "AVS IN SENATOR"
                print avs.count()
                avs = avs.filter(Q(demVoters__rep__repID__in=lsSenatorCodes)|Q(repVoters__rep__repID__in=lsSenatorCodes))
        
        if topicID=='all' and subtopicID=='all':
            newAVS=[]
            if not avs:
                avs = AnomVoters.objects.all().order_by('-vote__dateVote','-vote__number')
            for av in avs:
                if av.vote.amendment and av.vote.amendment.subtopics.all().count() > 0:
                    newAVS.append(av)
                elif not av.vote.amendment and av.vote.bill.subtopics.all().count() > 0:
                    newAVS.append(av)
            avs = newAVS
        
        
        elif topicID!='all' and subtopicID!='all':
            newAVS=[]
            if not avs:
                avs = AnomVoters.objects.all().order_by('-vote__dateVote','-vote__number')
            for av in avs:
                if av.vote.amendment and av.vote.amendment.subtopics.filter(code=subtopicID).count() > 0:
                    newAVS.append(av)
                elif not av.vote.amendment and av.vote.bill.subtopics.filter(code=subtopicID).count() > 0:
                    newAVS.append(av)
            avs = newAVS    
            
        elif subtopicID=='all' and topicID!='all':
            newAVS=[]
            if not avs:
                avs = AnomVoters.objects.all().order_by('-vote__dateVote','-vote__number')
            #print "AVS BEFORE TOPIC EXCLUSION"    
            #print avs.count()
            for av in avs:
                if av in newAVS:
                    continue
                    
                if av.vote.hasAmendment and av.vote.amendment.subtopics.filter(topic__code=topicID).count() > 0:
                    newAVS.append(av)
                elif av.vote.bill.subtopics.filter(topic__code=topicID).count() > 0:
                    newAVS.append(av)
            #print "NEW AVS"
            #print newAVS
            avs = newAVS
        
        newAVS2 = []    
        for av in avs:
            if av in newAVS2:
                continue
            newAVS2.append(av)
        
        print "NEW AVS2"
        print newAVS2
            
        dDescribe = {}
        #avs = avs.order_by('-vote__dateVote','-vote__number')
        i=0
        for av in newAVS2:
            if hasReport(av.vote):
                dDescribe[i] = av.vote.htmlDescript
                i+=1
                
        dRet={}
        dRet['html_descript'] = dDescribe
        return HttpResponse(simplejson.dumps(dRet), mimetype='application/json')

def about(request):
     t = loader.get_template('votes/about.html')
     c = Context({'refURL':ref_url})
     return HttpResponse(t.render(c))

def ccu_api(request):
  t = loader.get_template('votes/ccu_api.html')
  c = Context({})
  return HttpResponse(t.render(c))


def load_vote_xml(request,xml,session,bill_prefix,bill_number,vote_number):
         global ref_url

         vote = Vote.objects.filter(bill__congress__number=session,bill__prefix=bill_prefix,bill__number=bill_number,number=vote_number)[0]
         allVoters = []
         try:
             allVoters = [av for av in AnomVoters.objects.get(vote=vote).demVoters.all().order_by('rep__lastName')]
         except Exception,ex:
             print ex


         try:
             allVoters.extend([av for av in AnomVoters.objects.get(vote=vote).repVoters.all().order_by('rep__lastName')])
         except Exception,ex:
             pass

         biPartisan = []
         biPartTF=[]
         predElection=[]
         relComm = []
         naicsInd = []
         repContr = []
         pviReport = []

         if allVoters:
             for av in allVoters:
                 voter=av.rep
                 try:
                     biPartisan.append(RepWithPartyReport.objects.get(vote=vote,repWithParty__rep=voter).repWithParty)
                     biPartTF.append(True)
                 except Exception,ex:
                     try:
                         biPartisan.append(RepWithParty.objects.get(rep=voter,congress=voter.congress))
                         biPartTF.append(False)
                     except Exception:
                         obj,isThere = RepWithParty.objects.get_or_create(rep=voter,congress=voter.congress,withPartyScore=-1)
                         biPartisan.append(obj)
                         biPartTF.append(False)


                 try:
                     predElection.append(PredElectionReport.objects.get(vote=vote,predElection__rep=voter))
                 except Exception,ex:
                     predElection.append(None)
                 
                 try:
                     relComm.append(ChairCommitteeReport.objects.get(vote=vote,rep=voter))
                 except Exception,ex:
                     relComm.append(None)

                 try:
                     pviReport.append(StatePVIReport.objects.get(vote=vote,rep=voter))
                 except Exception:
                     pviReport.append(None)
                 
                 
                 naicsObjs = NAICSIndustryReport.objects.filter(vote=vote,rep=voter)
                 if naicsObjs.count() > 0:
                     naicsInd.append(naicsObjs)
                 else:
                     naicsInd.append([])

                 rcObjs = RepContributionReport.objects.filter(vote=vote,rep=voter)
                 if rcObjs.count() > 0:
                     repContr.append(rcObjs)
                 else:
                     repContr.append([])
                
         #print allVoters
         #print biPartisan
         #print predElection
         #print relComm
         #print naicsInd
         #print repContr
         t = loader.get_template('votes/one_vote.xml')
         c = Context({'refURL':ref_url,'vote':vote,'voters':zip(allVoters,biPartisan,biPartTF,predElection,relComm,naicsInd,repContr,pviReport)})
         return HttpResponse(t.render(c),content_type='application/xml',mimetype='application/xml')

def findVoterInf(dVoterInf,vote):
    
    numVoteDemNay = vote.repVotes.filter(voteCast='NAY',rep__party__istartswith='d').count()
    numVoteDemAye = vote.repVotes.filter(voteCast='AYE',rep__party__istartswith='d').count()
    
    numVoteRepNay = vote.repVotes.filter(voteCast='NAY',rep__party__istartswith='r').count()
    numVoteRepAye = vote.repVotes.filter(voteCast='AYE',rep__party__istartswith='r').count()
    
    voteMajDem = None
    voteMajRep=None
    
    if vote.question.lower().find('table') > -1 or vote.question.lower().find('cloture') > -1:
         if numVoteDemAye > numVoteDemNay:
               voteMajDem='Against'
               voteMinDem='For'
         else:
               voteMajDem = 'For'
               voteMinDem = 'Against'
         
         if numVoteRepAye > numVoteRepNay:
               voteMajRep='Against'
               voteMinRep='For'
         else:
               voteMajRep='For'
               voteMinRep='Against'
    else:
          if numVoteDemAye > numVoteDemNay:
                voteMajDem='For'
                voteMinDem='Against'
          else:
                voteMajDem = 'Against'
                voteMinDem = 'For'

          if numVoteRepAye > numVoteRepNay:
                voteMajRep='For'
                voteMinRep='Against'
          else:
                voteMajRep='Against'
                voteMinRep='For'

    if vote.hasAmendment:
       voteMajDem += ' amendment'
       voteMinDem += ' amendment'
       voteMajRep += ' amendment'
       voteMinRep += ' amendment'
    else:
       voteMajDem += ' bill'
       voteMinDem += ' bill'
       voteMajRep += ' bill'
       voteMinRep += ' bill'
    
    dVoterInf2={}
    for voter in dVoterInf:
       dVoterInf2[voter] = [dVoterInf[voter]]
       if voter.party.lower().find('d') > -1:
            dVoterInf2[voter].append(voteMinDem)
            dVoterInf2[voter].append(voteMajDem)
            
       else:
            dVoterInf2[voter].append(voteMinRep)
            dVoterInf2[voter].append(voteMajRep)
            
    return dVoterInf2 
     
def load_vote_refined(request,session,bill_prefix,bill_number,vote_number):
        global ref_url

        
        vote = Vote.objects.filter(bill__congress__number=session,bill__prefix=bill_prefix,bill__number=bill_number,number=vote_number)[0]
        tempReps = TempRepPoints.objects.filter(vote=vote).order_by('-points')
        allVoters=None
        if tempReps.count()>0:
            allVoters = [tr for tr in tempReps]
            if len(tempReps) > 5:
                allVoters = allVoters[0:5]
            allVoters = [av for av in allVoters if tempReps.filter(rep=av.rep)[0].points > 0]
        
        allVoters2 = []
        #uniqueify, blah...
        for voter in allVoters:
            if voter not in allVoters2:
                print 'ADDING'
                allVoters2.append(voter)
        
        allVoters = allVoters2
        #print 'TEMP REPS NOW'
        #print allVoters
        
        biPartisan = []
        predElection=[]
        relComm = []
        naicsInd = []
        repData = []
        pviReportDem = []
        pviReportRep = []
        dVoterInf={}
       
        oldMin=-22
        oldMax=15
        newMin=0
        newMax=100
        oldRange=oldMax-oldMin
        newRange=newMax-newMin
        
        if allVoters:
        
            for av in allVoters:
                #print av
                voter=av.rep
                dVoterInf[voter]=[]
                lsInf=[]      
                try:
                    predElection.append(PredElectionReport.objects.get(vote=vote,predElection__rep=voter))
                    lsInf.append('election')
                except Exception,ex:
                    pass
                    ##print ex
                    #predElection.append(None)

                #try:
                if voter.party=='D':
                    
                    try:
                        report=StatePVIReport.objects.get(vote=vote,rep=voter)
                        if report.statePVI.demCook:
                            pviDem=(((report.statePVI.scoreCook-oldMin)*newRange)/oldRange)+newMin
                        else:
                            oldVal = 0-report.statePVI.scoreCook
                            pviDem=(((oldVal-oldMin)*newRange)/oldRange)+newMin
                    
                        avgScore=(((report.averageScore-oldMin)*newRange)/oldRange)+newMin
                    
                        pviReportDem.append([report,int(pviDem),int(avgScore)])
                        lsInf.append('state_diff')
                    except Exception:
                        pass
                elif voter.party=='R':
                    try:
                        report=StatePVIReport.objects.get(vote=vote,rep=voter)
                        if report.statePVI.demCook:
                            pviRep=(((report.statePVI.scoreCook-oldMin)*newRange)/oldRange)+newMin
                        else:
                            oldVal = 0-report.statePVI.scoreCook
                            pviRep=(((oldVal-oldMin)*newRange)/oldRange)+newMin
                    
                        avgScore=(((report.averageScore-oldMin)*newRange)/oldRange)+newMin
                    
                        pviReportRep.append([report,int(pviRep),int(avgScore)])
                        lsInf.append('state_diff')
                    except Exception,ex:
                        pass

                try:
                    relComm.append(ChairCommitteeReport.objects.get(vote=vote,rep=voter))
                    lsInf.append('committee')
                except Exception,ex:
                    pass
                    ##print ex
                    #relComm.append(None)

                naicsObjs = NAICSIndustryReport.objects.filter(vote=vote,rep=voter)
                if naicsObjs.count() > 0:
                    lsInf.append('industry')
                    
                    for objR in naicsObjs:
                        objL = objR.naicsLocale
                        otherObjs = NAICS_Locale.objects.filter(naicsIndustry=objL.naicsIndustry,beginQuarter=objL.beginQuarter,beginYear=objL.beginYear,endQuarter=objL.endQuarter,endYear=objL.endYear)
                      
                        otherObjs = sorted(otherObjs,key=lambda p:p.percentage())
                        otherObjs.reverse()
                        print 'OTHEROBJS'
                        print otherObjs               
                        newObjs = []
                        otherStates=[]
                        otherPercents=[]
                        #i think this is hacky, but it works....
                        if len(otherObjs) <= 5:
                            newObjs = otherObjs[0:len(otherObjs)]
                        else:
                            #if in middle of array...
                            if objR.rank-3 >= 0 and objR.rank+2<=len(otherObjs):
                                newObjs = otherObjs[objR.rank-3:objR.rank+2]
                            elif objR.rank<=2:#if at beginning edge
                                newObjs = otherObjs[0:5]
                            elif objR.rank >= len(otherObjs)-1:
                                newObjs = otherObjs[len(otherObjs)-6:len(otherObjs)]
                            
                        for obj in newObjs:
                            stateName = obj.state.name.replace(' ','+').title()
                            otherStates.append(stateName)
                            otherPercents.append(round(obj.percentage(),2))
                        
                        naicsInd.append([objR,otherStates,otherPercents,round(otherPercents[0]*2,2)])
                        
                dVoterInf[voter].extend(lsInf)
        
      
        lsRep = []
        lsSector = []
        lsTotal = []
        lsPercent = []
        lsBuses=[]
        lsBusAmt=[]
        
        
        rcs = RepContributionReport.objects.filter(vote=vote,rep__in=[av.rep for av in allVoters])
        
        if rcs.count() > 0:
            reps = rcs.values_list('rep',flat=True)
            reps = list(set(reps))
            for rep in reps:
               dVoterInf[Rep.objects.get(pk=rep)].extend(['contribution'])
               rcs_rep = rcs.filter(rep=rep)
               sectors = list(set(rcs_rep.values_list('bus__industry__sector',flat=True)))
               for sector in sectors:
                   lsRep.append(Rep.objects.get(pk=rep))
                   lsSector.append(MapLightSector.objects.get(pk=sector))
                   rc_buses = rcs_rep.filter(bus__industry__sector=sector)
                   buses = list(set(rc_buses.values_list('bus',flat=True)))
                   lsB = [MapLightBusiness.objects.get(pk=bus) for bus in buses]
                   lsBuses.append(lsB)
                   lsAmt=[]
                   for bus in lsBuses[-1]:
                       amountBus = rc_buses.filter(bus=bus).aggregate(Sum('totalAmt'))['totalAmt__sum']
                       lsAmt.append(amountBus)
                   lsBusAmt.append(zip(lsB,lsAmt))    
                   lsTotal.append(rc_buses.aggregate(Sum('totalAmt'))['totalAmt__sum'])
                   totalAll = RepContributionTotalAmounts.objects.filter(endDate=vote.dateVote,rep=rep)[0].totalAmt
                   lsPercent.append((lsTotal[-1]/float(totalAll))*100)
            lsTotal = [convertMoney(total) for total in lsTotal]
        
            repContr = zip(lsPercent,lsRep,lsSector,lsTotal,lsPercent,lsBusAmt,lsBuses)
            repContr.sort()
            repContr.reverse()
            lsPercent,lsRep,lsSector,lsTotal,lsPercent,lsBusAmt,lsBuses = zip(*repContr)
            repContr = zip(lsRep,lsSector,lsTotal,lsBuses,lsPercent)        
        else:
            repContr=[]
            reps=[]
        
        lsAmtCompIntFor=[]
        lsAmtCompIntAgainst=[]
        lsAmtCompFor=[]
        lsAmtCompAgainst=[]
        lsCompSector=[]
        lsBreakdownFor=[]
        lsBreakdownAgainst=[]
        lsRepStance=[]
        lsRep0=[]
        rcs = RepContributionReport.objects.filter(vote=vote,rep__in=[av.rep for av in allVoters])
        if not vote.hasAmendment:         
           
           for rep in reps:
                print Rep.objects.get(pk=rep)
                rcs_rep = rcs.filter(rep=rep)
                sectors = list(set(rcs_rep.values_list('bus__industry__sector',flat=True)))
                for sector in sectors:
                    print sector
                    rc_buses = rcs_rep.filter(bus__industry__sector=sector)
                
                    amtCompFor=0
                    amtCompAgainst=0
                    lsCompaniesFor=[]
                    lsCompaniesAgainst=[]
                
                    for rc in rc_buses: 
                        print rc.amtMoneyFor
                        print rc.amtMoneyAgainst
                        if rc.amtMoneyFor != None:
                            amtCompFor += rc.amtMoneyFor
                        
                        if rc.amtMoneyAgainst !=None:
                            amtCompAgainst += rc.amtMoneyAgainst
                    
                      
                  
                    if amtCompFor > 0 or amtCompAgainst > 0:
                        try:
                            dVoterInf[Rep.objects.get(pk=rep)].extend(['company'])
                        except Exception:
                            dVoterInf[Rep.objects.get(pk=rep)] = ['company']
                    
                        lsRep0.append(Rep.objects.get(pk=rep))
                        #HERE PUT BREAKDOWN OF COMPANIES AND MONEY
                        #print sector
                    
                        #print "LOOKING AT RCOS"
                        rcos = RepOrgStanceMoneyVote.objects.filter(repReport__in=rc_buses,forVote=True)
                        #print rcos
                        if rcos.count() > 0:
                            dInds={}
                            for rco in rcos:
                                dInds[rco.orgst] = rco.totalAmt
                            lsBreakdownFor.append(dInds)
                        else:
                            lsBreakdownFor.append(None)
                
                        rcos = RepOrgStanceMoneyVote.objects.filter(repReport__in=rc_buses,forVote=False)
                        #print rcos
                        if rcos.count() > 0:
                            dInds={}
                            for rco in rcos:
                                dInds[rco.orgst] = rco.totalAmt
                            lsBreakdownAgainst.append(dInds)
                        else:
                            lsBreakdownAgainst.append(None)    
                                                
                        lsAmtCompIntFor.append(amtCompFor)
                        lsAmtCompIntAgainst.append(amtCompAgainst)
                        lsAmtCompFor.append(convertMoney(amtCompFor))
                        lsAmtCompAgainst.append(convertMoney(amtCompAgainst))
                        lsCompSector.append(MapLightSector.objects.get(pk=sector))
                        
                        billSponsorParty=None
                        if vote.bill:
                           billSponsorParty=vote.bill.sponsor.party.lower()
                        
                        repParty = Rep.objects.get(pk=rep).party.lower()
                        
                        #just a motion, everyone voting aye is for bill
                        if vote.question.lower().find('motion') > -1 and vote.question.lower().find('cloture')==-1:
                            if vote.repVotes.filter(rep=rep)[0].voteCast=='AYE':
                                lsRepStance.append(True)
                            else:
                                lsRepStance.append(False)
                        
                        elif vote.question.lower().find('cloture') > -1 and billSponsorParty!=repParty and billSponsorParty:
                            if vote.repVotes.filter(rep=rep)[0].voteCast=='AYE':
                                lsRepStance.append(True)
                            else:
                                lsRepStance.append(False)
                        elif vote.question.lower().find('cloture') > -1:
                           if vote.repVotes.filter(rep=rep)[0].voteCast=='AYE':
                                lsRepStance.append(False)
                           else:
                                lsRepStance.append(True)
                        else:
                            if vote.repVotes.filter(rep=rep)[0].voteCast=='AYE':
                                lsRepStance.append(True)
                            else:
                                lsRepStance.append(False)
                    
        #repOrgs = zip(lsAmtCompInt,lsAmtCompIntOpp,lsRep0,lsCompanyStance,lsCompanySame,lsAmtComp,lsAmtCompOpp,lsCompSector,lsBreakdownFor,lsBreakdownAgainst)         
        repOrgs = zip(lsAmtCompIntFor,lsAmtCompIntAgainst,lsRep0,lsRepStance,lsAmtCompFor,lsAmtCompAgainst,lsCompSector,lsBreakdownFor,lsBreakdownAgainst) 
        
        #print 'REPORGS'
        #print repOrgs
        repOrgs.sort()
        repOrgs.reverse()
      
        lsVoteChartCols=[['string','typeVote'],['number','numVotes']]
        lsVoteDemRows=[['AYE',vote.numDemsAye()],['NAY',vote.numDemsNay()],['NO VOTE',vote.numDemsNV()],['PRESENT',vote.numDemsPresent()]]
        lsVoteRepRows=[['AYE',vote.numRepsAye()],['NAY',vote.numRepsNay()],['NO VOTE',vote.numRepsNV()],['PRESENT',vote.numRepsPresent()]]
        lsVoteOtherRows=[['AYE',vote.numOtherAye()],['NAY',vote.numOtherNay()],['NO VOTE',vote.numOtherNV()],['PRESENT',vote.numOtherPresent()]]
        
        dVoterInf = findVoterInf(dVoterInf,vote)
        lsTop5Dem = []
        lsTop5Rep = []
        for av in allVoters:
            if av.rep.party.lower().find('d') > -1:
               lsTop5Dem.append([av.rep,dVoterInf[av.rep]])
            else:
               lsTop5Rep.append([av.rep,dVoterInf[av.rep]])
        #print lsTop5
        
        #print 'HERE3'
        t = loader.get_template('votes/one_vote_refined.html')
        c = Context({'lsRepContr':lsRep,'lsContrTables':lsBusAmt,'lsVoteChartCols':lsVoteChartCols,'lsVoteDemRows':lsVoteDemRows,'lsVoteRepRows':lsVoteRepRows,'lsVoteOtherRows':lsVoteOtherRows,'refURL':ref_url,'vote':vote,'lsTop5Dem':lsTop5Dem,'lsTop5Rep':lsTop5Rep,'repOrgs':repOrgs,'pviReportRep':pviReportRep,'pviReportDem':pviReportDem,'repContr':repContr,'naicsInd':naicsInd,'relComm':relComm,'predElect':predElection})
        return HttpResponse(t.render(c))
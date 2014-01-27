from django.db import models
import simplejson
from datetime import date,timedelta
from django.db.models import *
import sys
from ccu_utilities import *
from paths import *
from django import forms
from decimal import Decimal 

NUM_DAYS_CONTRIBUTION=730

try:
    partyPercentD = simplejson.load(open(CCU_DATA_PATH + 'partyPercentD.json'))
except Exception:
    partyPercentD = {}

try:
     industryPercentD = simplejson.load(open(CCU_DATA_PATH  + 'industryPercentD.json'))
except Exception:
    industryPercentD = {}
    
try:
    contrD = simplejson.load(open(CCU_DATA_PATH + 'contrD.json'))
except Exception:
    contrD = {}    

VOTE_CHOICES=(
    ('AYE','Aye'),
    ('NAY','Nay'),
    ('NV','No Vote'),
    ('PR','Present')
)

TITLE_CHOICES=(
    ('SHORT','Short'),
    ('OFFICIAL','Official')
)

TITLE_STATUS_CHOICES=(
    ('INTRODUCED','Introduced'),
    ('PASSED_HOUSE','Passed to the House'),
    ('PASSED_SENATE','Passed to the Senate'),
    ('ENACTED','Enacted'),
    ('REPORTED_TO_HOUSE','Reported to the House'),
    ('AMENDED_BY_HOUSE','Amended by the House'),
    ('REPORTED_TO_SENATE','Reported to the Senate'),
    ('AMENDED_BY_SENATE','Amended by the Senate')
)

BILL_STATUS_CHOICES=(
    ('ENACTED:SIGNED','ENACTED:SIGNED'),
    ('INTRODUCED','INTRODUCED'),
    ('REFERRED','REFERRED'),
    ('PASS_OVER:HOUSE','PASS_OVER:HOUSE'),
    ('PASS_BACK:SENATE','PASS_BACK:SENATE'),
    ('REPORTED','REPORTED'),
    ('PROV_KILL:SUSPENSIONFAILED','PROV_KILL:SUSPENSIONFAILED'),
    ('VETOED:OVERRIDE_FAIL_ORIGINATING:HOUSE','VETOED:OVERRIDE_FAIL_ORIGINATING:HOUSE'), 
    ('PASSED:CONCURRENTRES','PASSED:CONCURRENTRES'), 
    ('FAIL:ORIGINATING:HOUSE','FAIL:ORIGINATING:HOUSE'), 
    ('PASSED:SIMPLERES','PASSED:SIMPLERES'), 
    ('PASS_OVER:SENATE','PASS_OVER:SENATE'), 
    ('PROV_KILL:CLOTUREFAILED','PROV_KILL:CLOTUREFAILED'), 
    ('PASS_BACK:HOUSE','PASS_BACK:HOUSE'),
    ('PASSED:BILL','PASSED:BILL'), 
    ('FAIL:ORIGINATING:SENATE','FAIL:ORIGINATING:SENATE')
)


COMMITTEE_TYPE_CHOICES = (
    ('SENATE','Senate'),
    ('HOUSE','House'),
    ('JOINT','Joint')
)

PRED_ELEC_CHOICES=(
    ('SOLID_D','Very Likely Democrat will win'),
    ('LIKE_D','Likely Democrat will win'),
    ('LEAN_D','Lean Chance Democrat will win'),
    ('TU','Toss Up Who Will Win'),
    ('LEAN_R','Lean Chance Republican will win'),
    ('LIKE_R','Likely Republican will win'),
    ('SOLID_R','Very likely Republican will win'),
    ('RETIRE','Retiring'),
    ('RS','Running for Senate'),
    ('RG','Running for Governor'),
    ('RM','Running for Mayor'),
    ('PR','Potential Retirement'),
    ('PS','Potential Senate Candidate'),
    ('PG','Potential Governor Candidate'),
    ('PM','Potential Mayoral Candidate')
)

PARTY_CHOICES = (
    ('D','Democrat'),
    ('R','Republican'),
    ('I','Independent')
    )

GENDER_CHOICES = (
    ('M', 'Male'),
    ('F', 'Female'),
)

QUARTER_CHOICES = (
    (1,'Q1'),
    (2,'Q2'),
    (3,'Q3'),
    (4,'Q4'),
    )

def convertMoney(value):
	return moneyfmt(Decimal(str(value)),curr='$')

def moneyfmt(value, places=2, curr='', sep=',', dp='.',pos='', neg='-', trailneg=''):
    """Convert Decimal to a money formatted string.
    places:  required number of places after the decimal point
    curr:    optional currency symbol before the sign (may be blank)
    sep:     optional grouping separator (comma, period, space, or blank)
    dp:      decimal point indicator (comma or period)
             only specify as blank when places is zero
    pos:     optional sign for positive numbers: '+', space or blank
    neg:     optional sign for negative numbers: '-', '(', space or blank
    trailneg:optional trailing minus indicator:  '-', ')', space or blank

    >>> d = Decimal('-1234567.8901')
    >>> moneyfmt(d, curr='$')
    '-$1,234,567.89'
    >>> moneyfmt(d, places=0, sep='.', dp='', neg='', trailneg='-')
    '1.234.568-'
    >>> moneyfmt(d, curr='$', neg='(', trailneg=')')
    '($1,234,567.89)'
    >>> moneyfmt(Decimal(123456789), sep=' ')
    '123 456 789.00'
    >>> moneyfmt(Decimal('-0.02'), neg='<', trailneg='>')
    '<0.02>'

    """
    q = Decimal(10) ** -places      # 2 places --> '0.01'
    sign, digits, exp = value.quantize(q).as_tuple()
    result = []
    digits = map(str, digits)
    build, next = result.append, digits.pop
    if sign:
        build(trailneg)
    for i in range(places):
        build(next() if digits else '0')
    build(dp)
    if not digits:
        build('0')
    i = 0
    while digits:
        build(next())
        i += 1
        if i == 3 and digits:
            i = 0
            build(sep)
    build(curr)
    build(neg if sign else pos)
    return ''.join(reversed(result))

def groupedByTopic(self):
    dRet = {}
    lsTopics = self.subtopics.all().values('topic').distinct()
    #I know there is a better way to do this I just can't figure it out right now!
    for topicD in lsTopics:
        topicObj = JonesTopic.objects.filter(name=topicD['topic'])[0]
        dRet[topicObj] = []
        subtopics = self.subtopics.filter(topic=topicObj)
        for sub in subtopics:
            dRet[topicObj].append(sub)
    return dRet

class Congress(models.Model):
    number = models.IntegerField(primary_key=True)
    beginDate = models.DateField()
    endDate = models.DateField()
    def __unicode__(self):
        return str(self.number) + ' Congress'
        
    class Meta:
        verbose_name_plural = "Congressional Sessions"

class State(models.Model):
    #name = models.CharField(max_length=75,null=True,blank=True,primary_key=True)
    name = models.CharField(max_length=75,primary_key=True)
    abbrev = models.CharField(max_length=10,null=True,blank=True)

    def __unicode__(self):
        return self.name.title()
        
class District(models.Model):
    state = models.ForeignKey(State)
    districtNum = models.IntegerField(max_length=10)   
    
    def __unicode__(self):
        return str(self.state) + ' ' + str(self.districtNum)
    class Meta:
        unique_together = ['state','districtNum']
        
        
class StatePop(models.Model):
    state = models.ForeignKey(State)
    pop = models.IntegerField(max_length=10)
    date = models.DateField()
    
    def __unicode__(self):
        return str(self.state) + ' ' + str(self.pop) + ' ' + str(self.date)
    class Meta:
        unique_together = ['state','date']
        verbose_name_plural = "State Populations"
 
def pviProperString(self):
     strRet = ""
     if self.demCook: strRet += 'D+'
     else: strRet += 'R+'
     strRet += str(self.scoreCook)
     
     return strRet 
        
class StatePVI(models.Model):
    state = models.ForeignKey(State) 
    demCook = models.BooleanField(default=True) #demCook
    scoreCook = models.IntegerField() #scoreCook
    year = models.IntegerField() #year
    def __unicode__(self):
        strRet = str(self.state) + ':'
        return strRet + pviProperString(self)
    
    class Meta:
        verbose_name_plural = "State PVI"

class DistrictPVI(models.Model):
    district = models.ForeignKey(District) 
    demCook = models.BooleanField(default=True)
    scoreCook = models.IntegerField()
    year = models.IntegerField()
    def __unicode__(self):
        strRet = str(self.district) + ':'
        if self.demCook: strRet += 'D+'
        else: strRet += 'R+'
        strRet += str(self.scoreCook)
        strRet += ':' + str(self.year)
        return strRet
    class Meta:
        verbose_name_plural = "District PVI"
        
class JonesTopic(models.Model):
    name = models.CharField(max_length=250,primary_key=True)
    code = models.IntegerField(null=True,blank=True)
    def __unicode__(self):
        return self.name
    class Meta:
        verbose_name_plural = "Jones Topics"

class JonesSubTopic(models.Model):
    name = models.CharField(max_length=250)
    descript = models.TextField()
    topic = models.ForeignKey(JonesTopic)
    code = models.IntegerField(null=True,blank=True)
    
    def __unicode__(self):
        return self.topic.name + ':' + self.name
    class Meta:
        unique_together=['name','topic']   
        verbose_name_plural = "Jones Subtopics"
        
class MapLightSector(models.Model):
    name = models.CharField(max_length=100,primary_key=True)     
    officialName = models.CharField(max_length=100)
    code = models.IntegerField()

    def __unicode__(self):
        return self.name
    class Meta:
        verbose_name_plural = "Maplight Sectors"
        

class MapLightIndustry(models.Model):
    sector = models.ForeignKey(MapLightSector)
    name = models.CharField(max_length=100)
    code = models.IntegerField()
    
    def __unicode__(self):
        return self.name
    class Meta:
        unique_together=['name','sector'] 
        verbose_name_plural = "Maplight Industries"

class MapLightBusiness(models.Model):   
    industry = models.ForeignKey(MapLightIndustry)
    name = models.CharField(max_length=100)
    subtopics = models.ManyToManyField(JonesSubTopic,blank=True,null=True)
    mlID = models.CharField(max_length=50)

    def __unicode__(self):
        return str(self.industry.sector)+ ':' + str(self.industry) + ':' + self.name     
    class Meta:
        unique_together=['industry','name']
        verbose_name_plural = "Maplight Businesses"

def generateName(rep,creds=True,firstName=True,title=True):
    if not rep:
        return None

    name = ""
    if title and rep.senator == True: name = "Sen. "
    elif title:name = "Rep. "
    else: name=""

    if rep.nickName and rep.nickName != "" and firstName==True:
        name += "%s " % rep.nickName
    elif firstName==True:
        name += "%s " % rep.firstName

    name += rep.lastName
    if not rep.state and not rep.district:
        #print 'HERE'
        return name
    
    if rep.state:
        stateAbbrev = pyU.getStateAbbrev(rep.state.name)
    else:
        stateAbbrev = pyU.getStateAbbrev(rep.district.state.name)
    if creds:
        if rep.party.lower().find('d') > -1:
            name += ' [D,%s' % stateAbbrev
        elif rep.party.lower().find('r') > -1:
            name += ' [R,%s' % stateAbbrev
        else: #TODO: change this later to reflect labor party, etc.
            name += ' [I,%s' % stateAbbrev
        if not rep.senator and rep.district:
            name += '-%d]' % rep.district.districtNum
        else:
            name += ']'
    return  name


class Rep(models.Model):
    repID = models.CharField(max_length=50) #osID
    repGovTrackID = models.CharField(max_length=50) 
    congress = models.ForeignKey(Congress)

    firstName = models.CharField(max_length=50) #'''must have'''
    lastName = models.CharField(max_length=50) #'''must have'''
    nickName = models.CharField(max_length=50,null=True,blank=True)
    middleName = models.CharField(max_length=50,null=True,blank=True)
    
    party = models.CharField(choices=PARTY_CHOICES,max_length=2) #'''must have'''
    state = models.ForeignKey(State,null=True,blank=True)
    district = models.ForeignKey(District,null=True,blank=True)
    senator = models.BooleanField(default=True)
    senatorClass = models.IntegerField(null=True,blank=True)

    swornInDate = models.DateField() 
    endDate = models.DateField()
    website = models.CharField(max_length=200,null=True,blank=True)
    religion = models.CharField(max_length=50,null=True,blank=True)
    youtubeID = models.CharField(max_length=50,null=True,blank=True)
    twitterID = models.CharField(max_length=50,null=True,blank=True)
    address = models.TextField(null=True,blank=True)
    gender = models.CharField(choices=GENDER_CHOICES,max_length=2)
    birthday = models.DateField(null=True)

    #open congress
    imgURL = models.CharField(max_length=200,null=True,blank=True)


    def __unicode__(self):
        strRep = ""
        if self.senator: strRep = "Senator"
        else: strRep = "Representative"

        if self.senator:
            return str(self.congress) + ':' + self.lastName + ',' + self.firstName + ' ' + strRep + ' ' + str(self.state) + ' ' + str(self.party)
        else:
            return str(self.congress) + ':' + self.lastName + ',' + self.firstName + ' ' + strRep + ' ' + str(self.district) + ' ' + str(self.party)   
            
    class Meta:
        unique_together=['repID','congress']
    def officialPartyTitle(self):
        if self.party=='D':
            return 'Democrat'
        elif self.party=='R':
            return 'Republican'
        else:
            return 'Other'
    def officialName(self):
        return generateName(self,creds=True,firstName=True,title=True)
    def officialNameWOCred(self):
        return generateName(self,creds=False,firstName=True, title=False)
    
class RepADA(models.Model):
    rep = models.ForeignKey(Rep)
    adaScore = models.IntegerField()
    year = models.IntegerField()
    def __unicode__(self):
        return str(self.rep)  + ':' + str(self.adaScore) + '%:' + str(self.year)
    class Meta:
        unique_together = ['rep','year']

def addPartyPercentD(number):
    partyPercentD[number] = [rw.withPartyScore for rw in RepWithParty.objects.filter(congress__number=number,rep__senator=True)]
    partyPercentD[number].sort()
    simplejson.dump(partyPercentD,open(CCU_DATA_PATH + 'partyPercentD.json','w'))

class RepWithParty(models.Model):
    rep = models.ForeignKey(Rep)
    withPartyScore = models.IntegerField()
    congress = models.ForeignKey(Congress)
    def __unicode__(self):
        return str(self.rep)  + ':' + str(self.withPartyScore) + '%:' + str(self.rank()) + '/100'
    def rank(self):
        if self.congress.number not in partyPercentD:
            addPartyPercentD(self.congress.number)
        try:
            #print partyPercentD[self.congress.number]
            rank = partyPercentD[self.congress.number].index(self.withPartyScore)
            return rank + 1
        except Exception:
            return -1
        
    class Meta:
        unique_together = ['rep','congress']


            
class RepContribution(models.Model):
    rbID = models.CharField(primary_key=True,max_length=255)
    pubDate = models.DateTimeField()
    rep = models.ForeignKey(Rep)
    amountContr = models.FloatField(default=0)
    dateContr = models.DateField()
    contribName = models.CharField(max_length=500)
    contribID = models.CharField(max_length=500)
    mlBusiness = models.ForeignKey(MapLightBusiness)
    contribOcc = models.CharField(max_length=1000,null=True,blank=True)
    contribEmployer = models.CharField(max_length=1000,null=True,blank=True)
    contribState = models.ForeignKey(State,null=True)
    contribZipCode = models.CharField(max_length=10,null=True,blank=True)
    isPAC = models.BooleanField()
    def __unicode__(self):
        if self.contribZipCode:
            zipcode=self.contribZipCode
        else:
            zipcode="NOZIP"
        if self.contribName:
            contribName=self.contribName
        else:contribName="None"
        
        if self.contribEmployer:
            contribEmp = self.contribEmployer
        else: contribEmp="None"
        return contribName + ':' + contribEmp + ':' + str(self.dateContr) + ':' + str(self.amountContr) + ':' + str(self.contribID) + self.mlBusiness.name
            
        return str(self.rep)+ ':' + str(self.amountContr) + ':' + str(self.mlBusiness) + ':' + str(self.dateContr) + ':' + str(self.contribState) + ':' + str(self.isPAC) + ':' 
        
class NAICS_Industry(models.Model):
    code = models.CharField(max_length=10,primary_key=True)
    name = models.CharField(max_length=500)
    mlBusinesses = models.ManyToManyField(MapLightBusiness)
    subtopics = models.ManyToManyField(JonesSubTopic)
    mlDirectMapping = models.BooleanField(default=True)
    def __unicode__(self):
        return self.code + ' ' + str(self.name)
    class Meta:
        verbose_name_plural = "NAICS Industries"

class NAICS_Locale2(models.Model):
   state = models.ForeignKey(State,null=True,blank=True)
   numEmployees = models.IntegerField()
   numEmployeesTotal = models.IntegerField()
   naicsIndustry = models.ForeignKey(NAICS_Industry)
   beginQuarter = models.IntegerField(choices=QUARTER_CHOICES)
   beginYear = models.IntegerField()
   endQuarter = models.IntegerField(choices=QUARTER_CHOICES)
   endYear = models.IntegerField()
   def __unicode__(self):
       return str(self.state) + ':' + str(self.numEmployees) + ':' + str(self.naicsIndustry) + ':' + str(self.beginQuarter) + ':' + str(self.endQuarter) + ':' + str(self.beginYear) + ':' + str(self.endYear)

   def percentage(self):
       if self.state:
           try:
               popObj = StatePop.objects.filter(date__lte=self.endYear,state=self.state).order_by('-date')[0]
           except Exception:
               popObj = StatePop.objects.filter(state=self.state).order_by('-date')[0]
           pop = popObj.pop

           return (float(self.numEmployees) / float(pop)) * 100
       else:
           print 'FIX THIS IN NAICS LOCALE'
           assert 0

   class Meta:
       unique_together = ['state','naicsIndustry','beginQuarter','beginYear','endQuarter','endYear']
       verbose_name_plural = "NAICS Industries per State"
         
class NAICS_Locale(models.Model):
    state = models.ForeignKey(State,null=True,blank=True)
    numEmployees = models.IntegerField()
    naicsIndustry = models.ForeignKey(NAICS_Industry)
    beginQuarter = models.IntegerField(choices=QUARTER_CHOICES)
    beginYear = models.IntegerField()
    endQuarter = models.IntegerField(choices=QUARTER_CHOICES)
    endYear = models.IntegerField()
    def __unicode__(self):
        return str(self.state) + ':' + str(self.numEmployees) + ':' + str(self.naicsIndustry) + ':' + str(self.beginQuarter) + ':' + str(self.endQuarter) + ':' + str(self.beginYear) + ':' + str(self.endYear)
    
    def percentage(self):
        if self.state:
            try:
                popObj = StatePop.objects.filter(date__lte=self.endYear,state=self.state).order_by('-date')[0]
            except Exception:
                popObj = StatePop.objects.filter(state=self.state).order_by('-date')[0]
            pop = popObj.pop
            
            return (float(self.numEmployees) / float(pop)) * 100
        else:
            print 'FIX THIS IN NAICS LOCALE'
            assert 0
        
    class Meta:
        unique_together = ['state','naicsIndustry','beginQuarter','beginYear','endQuarter','endYear']
        verbose_name_plural = "NAICS Industries per State"

class Election(models.Model):
    date = models.DateField(primary_key=True)
    senateClass = models.IntegerField(null=True,blank=True)
    
    def __unicode__(self):
        if self.senateClass:
            return 'Election ' + str(self.date) + ':Senate Class ' + str(self.senateClass)
        else:
            return 'Election ' + str(self.date) 

def lookUpChoice(text,choice):
    for item in choice:
        if item[0] == text:
            return item[1]
    return None

            
class PredElection(models.Model):
    date =  models.DateField()
    election = models.ForeignKey(Election)
    rep = models.ForeignKey(Rep)
    pred = models.CharField(choices=PRED_ELEC_CHOICES,max_length=15)
    
    
    
    def __unicode__(self):
        return str(self.rep) + ':' + str(self.election) + ':Prediction date:' + str(self.date) + ':' + self.pred
    
    def longPred(self):
        return lookUpChoice(self.pred,PRED_ELEC_CHOICES)
    class Meta:
        unique_together=['date','rep','election','pred']
    
class Committee(models.Model):
    congress = models.ForeignKey(Congress) 
    name = models.CharField(max_length=50) #name of committee   
    code = models.CharField(max_length=10)   
    reps = models.ManyToManyField(Rep)
    chair = models.ForeignKey(Rep,related_name='chair',null=True,blank=True)
    rankingMember = models.ForeignKey(Rep,related_name='ranking_member',null=True,blank=True)
    viceChair = models.ForeignKey(Rep,related_name='vice_chair',null=True,blank=True)
    typeComm = models.CharField(choices=COMMITTEE_TYPE_CHOICES,max_length=20)
    topics = models.ManyToManyField(JonesTopic)
    
    class Meta:
        unique_together = ['congress','code']
    def __unicode__(self):
        return str(self.congress) + ':' + self.name



class BillStatus(models.Model):
    status = models.CharField(BILL_STATUS_CHOICES,max_length=50) #find out all choices...
    date = models.DateField()
    def __unicode__(self):
        return 'STATUS'
        #return str(self.status) + ':' + str(self.date)
        
    class Meta:
        unique_together = ['status','date']
    
class BillTitle(models.Model):
    title = models.TextField()
    typeTitle = models.CharField(TITLE_CHOICES,max_length=50) 
    whenTitle = models.CharField(TITLE_STATUS_CHOICES,max_length=50) 
    def __unicode__(self):
        return self.title + ':' + self.typeTitle + ':' + self.whenTitle
    
    class Meta:
        unique_together = ['title','typeTitle','whenTitle']




class BillSubject(models.Model):
    name = models.CharField(max_length=255,primary_key=True) 
    descript = models.TextField()
    subtopics = models.ManyToManyField(JonesSubTopic)    
    def __unicode__(self):
        return self.name
       
class Organization(models.Model):
    orgID = models.CharField(primary_key=True,max_length=50)
    orgName = models.CharField(max_length=500)
    mlBusiness = models.ForeignKey(MapLightBusiness)
    def __unicode__(self):
        return  self.orgName + ':' + str(self.orgID)

class OrgName(models.Model):
    org = models.ForeignKey(Organization)
    name = models.CharField(max_length=500)
    class Meta:
        unique_together = ['org','name']
    def __unicode__(self):
        return self.name + ':' + str(self.org)
        
class OrgStance(models.Model):
    org = models.ForeignKey(Organization)
    dateStance = models.DateField(null=True,blank=True)
    against = models.BooleanField()
    wholeCite = models.TextField()
    urlCite = models.CharField(max_length=300)
    class Meta:
        unique_together = ['org','dateStance','against','wholeCite','urlCite']
    def __unicode__(self):
        retStr = self.org.orgName
        if not self.against: retStr += ':FOR BILL'
        else: retStr += ':AGAINST BILL'
        return retStr
    
#later examine and refine this...
class Bill(models.Model):
    congress = models.ForeignKey(Congress) 
    billNum = models.CharField(max_length=20) #get billNum
    prefix = models.CharField(max_length=10)
    senate=models.BooleanField(default=True) #get senate or not
    number = models.IntegerField()
    popularTitle = models.CharField(max_length=500,null=True,blank=True)
    otherTitles = models.ManyToManyField(BillTitle,null=True,blank=True)
    status = models.ForeignKey(BillStatus,null=True,blank=True)
    sponsor = models.ForeignKey(Rep,related_name='sponsor',null=True,blank=True) #get the sponsor
    cosponsors = models.ManyToManyField(Rep,null=True,blank=True) #get the cosponsors
    committees = models.ManyToManyField(Committee,null=True,blank=True)
    subjects = models.ManyToManyField(BillSubject,null=True,blank=True)
    orgStances = models.ManyToManyField(OrgStance,null=True,blank=True)
    summary = models.TextField(null=True,blank=True)
    subtopicsAssigned=models.BooleanField(default=False)
    subtopics = models.ManyToManyField(JonesSubTopic) #get subtopics
    class Meta:
        unique_together = ['congress','billNum']
    def __unicode__(self):
        return str(self.congress) + ':' + self.billNum
    def title(self):
        if self.popularTitle and self.popularTitle != "":
            return self.popularTitle
        else:
            titles = self.otherTitles.filter(typeTitle="short")
            if len(titles) > 0:
                return titles[0].title
            titles = self.otherTitles.filter(typeTitle="official")
            if len(titles) > 0:
                return titles[0].title
            return None
    def cleanedSummary(self):
        return pyU.sXMLUnescape(self.summary)        
    def twoPartSummary(self):
        summary = self.cleanedSummary()
        lsSummary = summary.split(' ')
        if len(lsSummary) < 20:
            return [summary,None]
        else:
            firstPart = ' '.join(lsSummary[0:20])
            restPart = ' '.join(lsSummary[20:])
            return [firstPart,restPart]   
    def groupedByTopic(self):
        return groupedByTopic(self)
    
class AmendStatus(models.Model):
    status = models.TextField()
    statusDate = models.DateField(null=True,blank=True)
    def __unicode__(self):
        return str(self.status) + ':' + str(self.statusDate)
        
class Amendment(models.Model):
    bill = models.ForeignKey(Bill) #get bill number
    number = models.CharField(max_length=20) #get amendment number
    description = models.TextField(null=True,blank=True)
    purpose = models.TextField(null=True,blank=True)
    status = models.ManyToManyField(AmendStatus,null=True,blank=True)
    sponsor = models.ForeignKey(Rep,null=True,blank=True) #get sponsor
    sponsorComm = models.ForeignKey(Committee,null=True,blank=True)
    sequence = models.IntegerField(null=True,blank=True)
    offeredDate = models.DateField(null=True,blank=True)
    text = models.TextField(null=True,blank=True)
    subtopics = models.ManyToManyField(JonesSubTopic) #get subtopics
    subtopicsAssigned=models.BooleanField(default=False)
    class Meta:
        unique_together = ['number','bill']
    def __unicode__(self):
        return str(self.bill) + ':' + self.number
    def groupedByTopic(self):
        return groupedByTopic(self)
    def cleanedDescript(self):
        return pyU.sXMLUnescape(self.description)

class VoteCategory(models.Model):
    category = models.CharField(max_length=100,primary_key=True)
    def __unicode__(self):
        return self.category

class VoteType(models.Model):
    voteType = models.CharField(max_length=100,primary_key=True)
    def __unicode__(self):
        return self.voteType

class VoteResult(models.Model):
    voteResult = models.CharField(max_length=100,primary_key=True)
    def __unicode__(self):
        return self.voteResult

class RepVote(models.Model):
    voteCast = models.CharField(max_length=20,choices=VOTE_CHOICES)
    rep = models.ForeignKey(Rep)
    def __unicode__(self):
        return self.rep.lastName + ':' + self.voteCast
    class Meta:
        unique_together = ['voteCast','rep']

class Vote(models.Model):
    bill = models.ForeignKey(Bill)  #4. look up bill info
    number = models.IntegerField() #1. get vote number
    dateVote = models.DateField()
    hasAmendment = models.BooleanField() #2. look if amendment or bill
    amendment = models.ForeignKey(Amendment,null=True,blank=True) #3. look up amendment info
    category = models.ForeignKey(VoteCategory)
    voteType = models.ForeignKey(VoteType)    
    question = models.TextField()
    percentNeeded = models.FloatField()
    percentGotten = models.FloatField()
    numAye = models.IntegerField()
    numNay = models.IntegerField()
    numNV = models.IntegerField()
    numPresent = models.IntegerField()
    result = models.ForeignKey(VoteResult)
    subtopics = models.ManyToManyField(JonesSubTopic) 
    repVotes = models.ManyToManyField(RepVote,related_name='repVotes')
    active = models.BooleanField(default=True)
    topicAssigned = models.BooleanField(default=False)
    htmlDescript = models.TextField(null=True,blank=True)
    demPossTurn = models.BooleanField(default=False)
    repPossTurn = models.BooleanField(default=False)
    demExact = models.BooleanField(default=False)
    repExact = models.BooleanField(default=False)
    senateVote = models.BooleanField(default=False)
    
    class Meta:
        unique_together = ['bill','number']
    def __unicode__(self):
        return str(self.bill) + ':' + str(self.number) + ':' + str(self.dateVote)
    
    def numDemsAye(self):
        return self.repVotes.filter(rep__party='D',voteCast='AYE').count()
        
    def numRepsAye(self):
        return self.repVotes.filter(rep__party='R',voteCast='AYE').count()
    
    def numOtherAye(self):
        return self.repVotes.filter(voteCast='AYE').exclude(rep__party__in=['R','D']).count()
         
    def numDemsNay(self):
        return self.repVotes.filter(rep__party='D',voteCast='NAY').count()
            
    def numRepsNay(self):
        return self.repVotes.filter(rep__party='R',voteCast='NAY').count()      
    
    def numOtherNay(self):
        return self.repVotes.filter(voteCast='NAY').exclude(rep__party__in=['R','D']).count()
        
    def numDemsPresent(self):
        return self.repVotes.filter(rep__party='D',voteCast='PR').count()              
    
    def numRepsPresent(self):
        return self.repVotes.filter(rep__party='R',voteCast='PR').count() 
    
    def numOtherPresent(self):
        return self.repVotes.filter(voteCast='PR').exclude(rep__party__in=['R','D']).count()     
    
    def numDemsNV(self):
        return self.repVotes.filter(rep__party='D',voteCast='NV').count()                
    
    def numRepsNV(self):
        return self.repVotes.filter(rep__party='R',voteCast='NV').count()      
    
    def numOtherNV(self):
        return self.repVotes.filter(voteCast='NV').exclude(rep__party__in=['R','D']).count()
    
    
    
    
class AnomVoters(models.Model):
    vote = models.ForeignKey(Vote,primary_key=True)
    demVoters = models.ManyToManyField(RepVote,related_name='dem_voters')
    repVoters = models.ManyToManyField(RepVote,related_name='rep_voters')
    def __unicode__(self):
        retStr = str(self.vote) + ':NUM DEMS:' + str(self.demVoters.all().count()) + 'NUM REPS:' + str(self.repVoters.all().count())
        retStr += ','.join(self.demVoters.all()) + "\n"
        retStr += ",".join(self.repVoters.all()) + "\n\n"

class StatePVIReport(models.Model):
    vote = models.ForeignKey(Vote) #lookup by vote
    statePVI = models.ForeignKey(StatePVI) #follow to new class
    rep = models.ForeignKey(Rep) #lookup by rep
    averageScore = models.FloatField(default=0)
    def __unicode__(self):
           return str(self.vote) + ':' + str(self.statePVI) + ':' + str(self.rep)
    def properStrScore(self):
        return pviProperString(self.statePVI)
    
    def properStrScoreEscape(self):
        return pviProperString(self.statePVI).replace('+',"&#43;")
        
    def properStrAvg(self):
        #return 'stuff'
        intAvg = int(self.averageScore+0.5)
        if self.averageScore < 0:
            
            return 'R+' + str(abs(intAvg))
        else:
            return 'D+' + str(intAvg)
        
    def properStrAvgEscapes(self):
        return self.properStrAvg.replace('+',"&#43;")
        
    class Meta:
           unique_together = ['vote','statePVI','rep']
    

class RepWithPartyReport(models.Model):
    vote =  models.ForeignKey(Vote)
    repWithParty = models.ForeignKey(RepWithParty)
    def __unicode__(self):
        return str(self.vote) + ':' + str(self.repWithParty)
    class Meta:
        unique_together = ['vote','repWithParty']   

class PredElectionReport(models.Model):
    vote =  models.ForeignKey(Vote)
    predElection = models.ForeignKey(PredElection)
    def __unicode__(self):
        return str(self.vote) + ':' + str(self.predElection)
    class Meta:
        unique_together = ['vote','predElection']

class ChairCommitteeReport(models.Model):
    vote = models.ForeignKey(Vote) #lookup
    rep = models.ForeignKey(Rep) #anomalous rep
    committee = models.ForeignKey(Committee) # lookup committee table
    def __unicode__(self):
        return str(self.vote) + ':' + str(self.rep) + ':' + str(self.committee)
    def isChair(self):
        if self.committee.chair==self.rep:
            return True
        else:
            return False
    
    def isViceChair(self):
        if self.committee.viceChair==self.rep:
            return True
        else:
            return False
    
    def isRankingMember(self):
        if self.committee.rankingMember==self.rep:
            return True
        else:
            return False    
    
    class Meta:
        unique_together = ['vote','rep','committee']

def addIndustryPercentD(voterIndustry):
     print 'in industry function'
     lsAll = []
     for state in State.objects.all():
         objs = NAICS_Locale.objects.filter(naicsIndustry=voterIndustry.naicsIndustry,state=state).order_by('-endYear')
     
         if objs.count() > 0:
             lsAll.append(objs[0].percentage())
         else: 
             lsAll.append(0)

     lsAll.sort()
     strLookup = getLookupStrInd(voterIndustry)
     industryPercentD[strLookup] = lsAll
     simplejson.dump(industryPercentD,open(CCU_DATA_PATH + 'industryPercentD.json','w'))     

def getLookupStrInd(voterIndustry):
    return str(voterIndustry.naicsIndustry)
        
class NAICSIndustryReport(models.Model):
    vote = models.ForeignKey(Vote)
    rep = models.ForeignKey(Rep)
    naicsLocale = models.ForeignKey(NAICS_Locale)
    rank = models.IntegerField()
    class Meta:
        unique_together = ['vote','rep','naicsLocale']
    def __unicode__(self):
        return str(self.vote.number) + ':' + str(self.rep) + ':' + str(self.naicsLocale)    
    def percentage(self):
        return self.naicsLocale.percentage()
 

def addContrD(vote,rep,bus,oldDate):
    #oldDate = vote.dateVote-timedelta(days=NUM_DAYS_CONTRIBUTION)
    lookupStr = getLookUpStrContr(vote,bus,oldDate)
    #sprint lookupStr
    lsTotalAmt = []
    #print vote.bill.congress.number
    for rep in Rep.objects.filter(congress=vote.bill.congress.number,senator=True):
         #try:
             #print rep
         #except Exception:
             #pass
         if RepContribution.objects.filter(rep=rep,dateContr__lte=vote.dateVote,dateContr__gte=oldDate,mlBusiness=bus).count() > 0:
             contrObjs = RepContribution.objects.filter(rep=rep,dateContr__lte=vote.dateVote,dateContr__gte=oldDate,mlBusiness=bus)
             totalAmt = contrObjs.aggregate(Sum('amountContr'))['amountContr__sum']
             lsTotalAmt.append(totalAmt)
             #print totalAmt
         else:
             lsTotalAmt.append(0)
             #print 0
     
    lsTotalAmt.sort()
    #print lsTotalAmt
    contrD[lookupStr] = lsTotalAmt
    simplejson.dump(contrD,open(CCU_DATA_PATH + 'contrD.json','w'))

def getLookUpStrContr(vote,mlBusiness,oldDate):
    #oldDate = vote.dateVote - timedelta(days=NUM_DAYS_CONTRIBUTION)
    lookupStr = mlBusiness.name + ':' + str(vote.dateVote) + ':' + str(oldDate)
    return lookupStr

class RepContributionTotalAmountsBus(models.Model):
    bus = models.ForeignKey(MapLightBusiness)
    rcs = models.ManyToManyField(RepContribution)
    totalAmt = models.IntegerField(default=0)
    rep = models.ForeignKey(Rep)
    endDate = models.DateField()

class RepContributionTotalAmounts(models.Model):
    rep = models.ForeignKey(Rep)
    endDate = models.DateField()
    totalAmt = models.IntegerField(default=0)
    rcs =  models.ManyToManyField(RepContribution)
    class Meta:
        unique_together = ['rep','endDate']
    def __unicode__(self):
        return str(self.endDate) + ':' + str(self.totalAmt)

class RepContributionAverage(models.Model):
    #beginDate = models.DateField()
    endDate = models.DateField()
    totalAmt = models.IntegerField()
    numReps = models.IntegerField()
    rcs = models.ManyToManyField(RepContribution)
    bus = models.ForeignKey(MapLightBusiness)
    class Meta:
        unique_together = ['bus','endDate']
    def __unicode__(self):
        return str(self.endDate) + ':' + str(self.bus) + ':' + str(self.totalAmt/float(self.numReps))


#Contributions made to anonymous voters       
class RepContributionReport(models.Model):
    vote = models.ForeignKey(Vote) #look up by vote
    rep = models.ForeignKey(Rep) #look up by anomalous voter
    endDate = models.DateField()
    bus = models.ForeignKey(MapLightBusiness) #business type
    totalAmt = models.IntegerField() #total amount
    rcs = models.ManyToManyField(RepContribution,related_name='all_rcs')
    #percent = models.FloatField()
    
    #orgStanceMapping = models.BooleanField()
    orgstancesFor = models.ManyToManyField(OrgStance,related_name='orgstance_for')
    orgstancesAgainst=models.ManyToManyField(OrgStance,related_name='orgstance_against')
    relRCSFor = models.ManyToManyField(RepContribution,related_name='rc_for')
    relRCSAgainst=models.ManyToManyField(RepContribution,related_name='rc_against')
    amtMoneyFor = models.FloatField(default=0)
    amtMoneyAgainst=models.FloatField(default=0)    
    obeyedCompany = models.BooleanField()

    def __unicode__(self):
        return str(self.rep) + ':' + str(self.bus.industry.sector) 
        #return str(self.totalAmt) + ':' + str(self.rep) + ':' + str(self.bus) + ':' + str(self.endDate)         

class RepOrgStanceMoneyVote(models.Model):
    repReport = models.ForeignKey(RepContributionReport)
    orgst = models.ForeignKey(OrgStance)
    rcs = models.ManyToManyField(RepContribution)
    totalAmt = models.IntegerField()
    forVote = models.BooleanField(default=False)
    class Meta:
        unique_together = ['repReport','orgst']
    def __unicode__(self):
        return str(self.repReport.vote) + ':' + str(self.orgst) + ':' + str(self.totalAmt) + ':' + str(self.repReport.rep)

class VoteReport(models.Model):
    hasInd = models.BooleanField(default=False)
    hasContr = models.BooleanField(default=False)
    hasOrgs = models.BooleanField()
    hasComm = models.BooleanField(default=False)
    hasDiff = models.BooleanField(default=False)
    hasElec = models.BooleanField(default=False)
    hasStance = models.BooleanField(default=False)
    vote = models.ForeignKey(Vote,primary_key=True)
    def __unicode__(self):
        return str(self.vote) + ':' + str(self.hasInd)

#GET ALL VOTERS WHO VOTED AGAINST PARTY    
def getAllAnomVoters(vote):
    allVoters=[]
    try:
        allVoters = [av for av in AnomVoters.objects.get(vote=vote).demVoters.all().order_by('rep__lastName')]  
        allVoters.extend([av for av in AnomVoters.objects.get(vote=vote).repVoters.all().order_by('rep__lastName')])
    except Exception,ex:
        #print ex
        return None
        
    return allVoters
    
class PercentWithParty(models.Model):
    rep = models.ForeignKey(Rep)
    subtopic = models.ForeignKey(JonesSubTopic)
    numWithParty = models.IntegerField(default=0)
    numVotes = models.IntegerField(default=0)
    lastVoteDate = models.DateField()
    class Meta:
        unique_together = ['rep','subtopic','lastVoteDate']
    def percentage(self):
        if self.numWithParty == 0 or self.numVotes==0:
            return 0
            
        return (self.numWithParty/float(self.numVotes)) * 100
    def __unicode__(self):
        return str(self.rep) + ':' + str(self.subtopic) + ':' + str(self.lastVoteDate) + ':' +str(self.numWithParty)+':' + str(self.numVotes) + ':' + str(self.percentage())
    

class PercentWithPartyStats(models.Model):
    subtopic = models.ForeignKey(JonesSubTopic)
    median=models.FloatField(default=0)
    mean = models.FloatField(default=0)
    std = models.FloatField(default=0)
    high_range=models.FloatField(default=0)
    low_range=models.FloatField(default=0)
    lastVoteDate = models.DateField()
    class Meta:
        unique_together = ['subtopic','lastVoteDate']
    def __unicode__(self):
        return str(self.subtopic) + ':' + str(self.lastVoteDate) + ':' + str(self.mean) + ':' + str(self.median) + ':' + str(self.std) + ':' + str(self.high_range) + ':' + str(self.low_range)
    

class TempRepPoints(models.Model):
    rep = models.ForeignKey(Rep)
    vote = models.ForeignKey(Vote)
    points = models.IntegerField(default=0)
    class Meta:
        unique_together = ['rep','vote']    
    def __unicode__(self):
        return str(self.rep) + ":" + str(self.points) + ":" + str(self.vote)
    
        
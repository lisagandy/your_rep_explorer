from ccu_utilities import *
from ccu_gen_beta.models import *
import dircache
from BeautifulSoup import BeautifulSoup
import xml
from datetime import date
from wikipedia_scraper import *
from paths import *
import string
import datetime

def loadBasicBillInfo(sessionNum):
    congressObj = Congress.objects.get(number=sessionNum)
    #keepGoing = False
    for fileName in dircache.listdir(CCU_DATA_PATH + '%d_bills/' % sessionNum):
       
        begin = datetime.datetime.now()
        print fileName
        senate=True
        if fileName.find('h') > -1:
            senate=False
            
            
        try:
            billNum = fileName.split('.xml')[0]
            if Bill.objects.filter(billNum=billNum,congress=congressObj,senate=senate).count() > 0:
                print 'FOUND'
                continue
            else:
                bill = Bill.objects.filter(billNum=billNum,congress=congressObj)[0]
                bill.senate = senate
                bill.save()
                print 'Processing %s' % billNum
        except Exception,ex:
            print ex
            #assert 0
        
        #continue
        
        if billNum.find('DS') > -1:
            print 'DS_Store file'
            continue
         
        senate=True   
        if billNum.find('sr') > -1:
            prefix = 'sr'
            number = int(billNum.split('sr')[1].split('.xml')[0])
        elif billNum.find('sc') > -1:
            prefix = 'sc'
            number = int(billNum.split('sc')[1].split('.xml')[0])
        elif billNum.find('sj') > -1:
            prefix = 'sj'
            number = int(billNum.split('sj')[1].split('.xml')[0])
        elif billNum.find('hr') > -1:
               prefix = 'hr'
               number = int(billNum.split('hr')[1].split('.xml')[0])
               senate=False
        elif billNum.find('hc') > -1:
               prefix = 'hc'
               number = int(billNum.split('hc')[1].split('.xml')[0])
               senate=False
        elif billNum.find('hj') > -1:
               prefix = 'hj'
               number = int(billNum.split('hj')[1].split('.xml')[0])
               senate=False
        elif billNum.find('s') > -1:
           try: #for crazy files like DS_Store
               prefix = 's'
               number = int(billNum.split('s')[1].split('.xml')[0])
           except Exception,ex:
               print ex
               continue
        else:
           try: #for crazy files like DS_Store
               prefix = 'h'
               senate=False
               number = int(billNum.split('h')[1].split('.xml')[0])
           except Exception,ex:
               print ex
               continue       
        
        
        xml = open(CCU_DATA_PATH + '/%d_bills/%s' % (sessionNum,fileName))
        doc = BeautifulSoup(xml)
           
        summary = doc.find('summary').string
        print 'HERE'
        
        popularTitle = None
        try:
            popularTitle = doc.find('titles').find('title',{'type':'popular'}).string
        except Exception:
            pass
        
        lsOtherTitles = []
        titleDoc = doc.find('titles').findAll('title')
        for titleTag in titleDoc:
            try:
                lsOtherTitles.append(BillTitle.objects.get_or_create(title=titleTag.string,typeTitle=titleTag['type'],whenTitle=titleTag['as'])[0])
            except Exception:
                continue
                
      
        print 'SPONSOR'
        sponsorObj = None
        try:
            sponsorObj = Rep.objects.get(repGovTrackID=doc.find('sponsor')['id'],congress=congressObj)
        except Exception:
            print "WHY NO SPONSOR?"
        
        print 'COSPONSOR'        
        lsCoSponsor = []
        for person in doc.findAll('cosponsor'):
            try:
                lsCoSponsor.append(Rep.objects.get(repGovTrackID=person['id'],congress=congressObj))
            except Exception:
                print "WHY NO REP FOR %s" % person
                
        lsCommittees = []
        for committee in doc.findAll('committee'):
            try:
                lsCommittees.append(Committee.objects.get(code=committee['code'].split('-')[0],congress=congressObj))
            except Exception:
                print "WHY NO COMMITTEE FOR %s" % committee
        
        print 'BEFORE BILL'      
        try:         
            bill,isThere = Bill.objects.get_or_create(prefix=prefix,billNum=billNum,number=number,congress=congressObj,senate=senate,sponsor=sponsorObj)
        except Exception,ex:
            bill = Bill.objects.filter(prefix=prefix,billNum=billNum,number=number,congress=congressObj)[0]
            bill.senate=senate
            bill.save()
            
        print 'SAVING SUMMARY'
        bill.summary = summary
        
        #bill.status = statusObj
        bill.popularTitle = popularTitle
        bill.sponsor = sponsorObj
        [bill.otherTitles.add(title) for title in lsOtherTitles]
        [bill.cosponsors.add(rep) for rep in lsCoSponsor]
        [bill.committees.add(co) for co in lsCommittees]
        bill.save()
        print bill
        print ""
        end = datetime.datetime.now()
        delta = end-begin
        print delta.seconds
        print delta.microseconds
        assert 0
# 
# def downloadOrgStanceBill(sessionNum):
#     url = "http://maplight.org/services_open_api/map.bill_positions_v1.xml?apikey=2d51847e72197478e8f763d81fcf618c&jurisdiction=us&session=%d&prefix=%s&number=%d"
#     reParen = re.compile("\(.*?\)")
#     reURL = re.compile('href=".*?"')
#     #found=False
#     
#     for i,bill in enumerate(Bill.objects.filter(congress__number=sessionNum)):
#         
#         #if already have stance of organizations for bill continue
#         #if bill.prefix.find('h') > -1: continue
#         # if bill.prefix=='hj' and bill.number==36:
#         #             found=True
#         
#         # if not found:
#         #             continue
#         print i
#         if bill.orgStances.all().count() > 0:
#             continue
#         
#         #print bill
#         urlFull = url % (sessionNum,bill.prefix,bill.number)
#         #print urlFull
#         
#         #print 'downloading file'
#         xmlStr = pyU._getFile(urlFull)
#         #print 'making doc'
#         doc = BeautifulSoup(xmlStr)
#     
#         for org in doc.findAll('organization'):
#             print org.find('name').string
#             print "--------------------------------"
# 
#             orgObj = None
# 
#             if not org.disposition.string:
#                 print "NO OPPOSE/FOR BLAH!!!"
#                 continue
#             
#             try:
#                 
#                 orgObj = Organization.objects.get(orgID=org.organization_id.string)
#                 
#                 
#             except Exception:
# 
#                 if not org.find('catcode').string:
#                     print 'NO CATCODE FOR THIS ORGANIZATION'
#                     continue
# 
#                 try:
#                     mlBusiness = MapLightBusiness.objects.get(mlID=org.find('catcode').string)
#                 except Exception:
#                     #print 'WHY NO BUSINESS FOR CATCODE %s ???????' % org.catcode.string
#                     continue
#                 
#                 orgName = xml.sax.saxutils.unescape(org.find('name').string).replace('&quot;','"').replace('&#039;','')
#                 print 'FOUND ORGNAME AND ESCAPED'
#                 print orgName
#                 print org.organization_id.string
#                 print mlBusiness
#                 orgObj = Organization()
#                 orgObj.orgID = str(org.organization_id.string)
#                 print 'orgid'
#                 orgObj.orgName = orgName
#                 print 'orgname'
#                 orgObj.mlBusiness = mlBusiness
#                 print 'MLBUSINESS'
#                 orgObj.save()
#                 print 'DONE'
#                 #orgObj = Organization.objects.get_or_create(orgID=org.organization_id.string,orgName=orgName,mlBusiness=mlBusiness)[0]
#                 
#     
#             print 'HERE AFTER MAKING ORG OBJECT'
#             orgStanceObj = OrgStance()
#             print 'MAKING A NEW ORGSTANCE'
#             orgStanceObj.org = orgObj
#             citation = xml.sax.saxutils.unescape(org.citation.string).replace('&quot;','"')
#             print 'finished citation'
#             orgStanceObj.wholeCite = citation
#             if org.disposition.string.find('oppo') > -1: orgStanceObj.against = True
#             else: orgStanceObj.against = False
#             
#             lsDate = reParen.findall(citation)
#             print 'HERE 2'
#             if len(lsDate) > 0 and lsDate[0].find('n.') == -1:
#                 dateStance = lsDate[0].replace('(','').replace(')','')
#                 #print 'IN DATE'
#                 #print dateStance
#                 try:
#                     print dateStance
#                     orgStanceObj.dateStance = createDate4(dateStance)
#                     
#                 except Exception,ex:
#                     #print ex
#                     try:
#                         orgStanceObj.dateStance = date(int(dateStance),1,1)
#                     except Exception,ex:
#                         print 'EXCEPTION IN DATE'
#                         continue
#                     #sometimes weird date issues, don't want to mess up whole save...
#                     
#             print 'finding url cite'        
#             try:
#                 orgStanceObj.urlCite = reURL.findall(citation)[0].replace('href=','').replace('"','')
#             except Exception:
#                 print 'PROBLEM WITH URL CITE'
#                 
#             try:
#                 orgStanceObj.save()
#             except Exception:
#                 orgStanceObj = OrgStance.objects.get(urlCite=orgStanceObj.urlCite,dateStance=orgStanceObj.dateStance,wholeCite=orgStanceObj.wholeCite,org=orgStanceObj.org,against=orgStanceObj.against)
#                 
#             
#             if orgStanceObj in bill.orgStances.all():
#                 print 'orgstance already there for this bill'
#                 continue
#                    
#             bill.orgStances.add(orgStanceObj)
#             print 'SAVING ORGSTANCE TO BILL'
#             try:
#                 print bill.orgStances.all()
#             except Exception,ex:
#                 print ex
#                 print "TROUBLE PRINTING"
#                 bill.save()
#             
# def removeExtraDashSpace(name):
#     if name.find('- ') > -1:
#         return name.replace('- ','-')
#     else:
#         return name
# 
# def removePunctuation(text, spaces = True,lsExcept=[]):
#     """
#     Removes punctuation from a string.
# 
#     @type text: C{string}
#     @param text: a string with punctuation.
# 
#     @rtype: C{string}
#     @return: the string without punctuation.
#     """
#     text = toascii(text)
#     spacePunctuation = ["'",'-','_','=','+','/','\\']
#     noSpacePunctuation = ['.','?','!',',',':',';','(',')','[',']','{','}','@','#','$','%','^','&','*','"']
# 
#     if spaces:
#         for punct in spacePunctuation:
#             if punct not in lsExcept:
#                 text = text.replace(punct,' ')
#     else:
#         for punct in spacePunctuation:
#             if punct not in lsExcept:
#                 text = text.replace(punct,'')
#     for punct in noSpacePunctuation:
#         if punct not in lsExcept:
#             text = text.replace(punct,'')
# 
#     return removeExtraDashSpace(stripExtraSpaces(text.strip(' ')))
# 
# 
# def removeWords(name):
#     name = removePunctuation(name,spaces=True,lsExcept=['-'])
#     name = name.replace('of','')
#     name = name.replace('the','')
#     name = name.replace('for','')
#     name = name.replace('&','')
#     name = name.replace('inc','')
#     name = name.replace('and','')
#     name = removeExtraDashSpace(stripExtraSpaces(name))
#     return name
# 
# def makeAbbreviation(name):
#     name = removeWords(name)
#     name2 = ''
#     if name.find('-') > -1:
#         name2 = name.split('-')[0] + '-'
# 
# 
#     lsName = name.split()
#     if len(lsName) < 3:
#         return None
#     else:
#         abbrev = ''.join([word[0] for word in lsName])
#         return name2 + abbrev
# 
# def removePunct(name):
#     name2 = removePunctuation(name,lsExcept=['-'])
#     if name2==name:
#         return None
#     else:
#         return removeExtraDashSpace(removeExtraDashSpace(stripExtraSpaces(name2)))
# 
# def removeInc(name):
#     if name.find('inc') > -1:
#         name2 = removePunctuation(name,lsExcept=['-'])
#         name2 = name2.replace('inc','')
#         name2 = removeExtraDashSpace(stripExtraSpaces(name2))
#         return name2
#     else:
#         return None
# 
# def removeLLP(name):
#     if name.find('llp') > -1:
#         name2 = removePunctuation(name,lsExcept=['-'])
#         name2 = name2.replace('inc','')
#         name2 = removeExtraDashSpace(stripExtraSpaces(name2))
#         return name2
#     else:
#         return None
# 
# def justAbbrev(name):
#     name = removeWords(name)
#     if name.find('-') > -1:
#         return None
#     else:
#         name2=''
#         for char in name:
#             if char in string.uppercase:
#                name2+=char
#             else:
#                 break     
#         if len(name2) > 2:
#             return name2
#         else:
#             return None
# 
# def removeDash(name):
#     if name.find('-') > -1:
#         return name.replace('-',' ')
#     else:
#         return None
# 
# 
# #print justAbbrev('CNP Action, Inc.')
# 
# 
# def changeAssoc(name,punct=True):
#     if not punct:
#         name2 = removePunctuation(name,lsExcept=['-'])
#     else:
#         name2 = name
# 
#     if name2.find('association') > -1:
#         name2 = name2.replace('association','assn')
#         return name2
#     elif name2.find('assn') > -1:
#         name2 = name2.replace('assn','association')
#         return name2
#     else:
#         return None
# 
# 
# def reconcileOrgs():
# 
# 
#     for i,org in enumerate(Organization.objects.all().order_by('orgName')):
# 
#         name = org.orgName
# 
#         name = name.lower()
#         name = toascii(name)
#         origName = stripExtraSpaces(name)
#         origName = name.strip()
#         org.orgName = org.orgName.strip()
#         org.save()
#         business = org.mlBusiness
# 
#         try:
#             abbrevName = makeAbbreviation(name)
#             if abbrevName and abbrevName!=origName and RepContribution.objects.filter(Q(contribEmployer__iexact=abbrevName)|Q(contribName__iexact=abbrevName),mlBusiness=business)[:1].count() > 0:
#                 og,isThere = OrgName.objects.get_or_create(name=abbrevName,org=org)
# 
# 
#             noIncName = removeInc(name)
#             if noIncName and noIncName!=origName and RepContribution.objects.filter(Q(contribEmployer__iexact=noIncName)|Q(contribName__iexact=noIncName),mlBusiness=business)[:1].count() > 0:
#                 OrgName.objects.get_or_create(name=noIncName,org=org)
# 
#             justAbbrevName = justAbbrev(org.orgName)
#             if justAbbrevName and justAbbrevName!=origName and RepContribution.objects.filter(Q(contribEmployer__iexact=justAbbrevName)|Q(contribName__iexact=justAbbrevName),mlBusiness=business)[:1].count() > 0:
#                 OrgName.objects.get_or_create(name=justAbbrevName,org=org)
# 
#             noPunctName = removePunct(name)
#             if noPunctName and noPunctName!=origName and RepContribution.objects.filter(Q(contribEmployer__iexact=noPunctName)|Q(contribName__iexact=noPunctName),mlBusiness=business)[:1].count() > 0:
#                 OrgName.objects.get_or_create(name=noPunctName,org=org)
# 
#             changeAssocName = changeAssoc(name,punct=True)
#             if changeAssocName and changeAssocName!=origName and RepContribution.objects.filter(Q(contribEmployer__iexact=changeAssocName)|Q(contribName__iexact=changeAssocName),mlBusiness=business)[:1].count() > 0:
#                 OrgName.objects.get_or_create(name=changeAssocName,org=org)
# 
#             changeAssocName2 = changeAssoc(name,punct=False)    
#             if changeAssocName2 and changeAssocName!=changeAssocName2 and changeAssocName2!=origName and RepContribution.objects.filter(Q(contribEmployer__iexact=changeAssocName2)|Q(contribName__iexact=changeAssocName2),mlBusiness=business)[:1].count() > 0:
#                 OrgName.objects.get_or_create(name=changeAssocName2,org=org)
# 
#             nollpName = removeLLP(name)
#             if nollpName and nollpName!=origName and RepContribution.objects.filter(Q(contribEmployer__iexact=nollpName)|Q(contribName__iexact=nollpName),mlBusiness=business)[:1].count() > 0:
#                 OrgName.objects.get_or_create(name=nollpName,org=org)
# 
#             removeDashName = removeDash(name)
#             if removeDashName and removeDashName!=origName and RepContribution.objects.filter(Q(contribEmployer__iexact=removeDashName)|Q(contribName__iexact=removeDashName),mlBusiness=business)[:1].count() > 0:
#                 OrgName.objects.get_or_create(name=removeDashName,org=org)
# 
#             if OrgName.objects.filter(org=org)[:1].count() > 0:
#                 print 'ORIGINAL ORG NAME'  
#                 print origName
#                 print
#                 print 'RESULTS'
#                 try:
#                     for on in OrgName.objects.filter(org=org):
#                         print on
#                     print ""
#                 except Exception:
#                     pass
# 
#         except Exception,ex:
#             print ex
# 
#             for i,bill in enumerate(Bill.objects.all()):
#                 try:
#                     if i % 9 == 0:
#                         time.sleep(5)

# def downloadBillTitles(session):
#     for bill in Bill.objects.filter(congress__number=session)    
#         try:
#         #xml = pyU._getFile('http://api.opencongress.org/bills?number=%s&type=%s&congress=%d' % (bill.number,bill.prefix,bill.congress.number))
#             xml = urllib.urlopen('http://api.opencongress.org/bills?key=65b43c3e67d6af4561b9ccac20e3f8f5f1325915&number=%s&type=%s&congress=%d' % (bill.number,bill.prefix,bill.congress.number)).read()
#             doc = BeautifulSoup(xml)
#             title=doc.find('bill').find('title-common').string
#             print title
#             bill.popularTitle = title
#             bill.save()
#         except Exception,ex:
#             print ex
            
if __name__ == '__main__':
    #Bill.objects.filter(number=3426,prefix="s").delete()
    #assert 0
    #loadBasicBillInfo(111)
    loadBasicBillInfo(112)
    #downloadOrgStanceBill(112)
    #downloadOrgStanceBill(111)
    #reconcileOrgs()
    #downloadBillTitles(111)
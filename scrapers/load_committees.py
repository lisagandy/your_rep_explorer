from ccu_gen_beta.models import *
from BeautifulSoup import BeautifulSoup
import pyUtilities as pyU
import re
import datetime

def mapCommitteesToTopics():
    #Used to map committees to Jones Topics
    dCT = {}
    dCT['House Committee on Agriculture:HSAG'] = [4]
    dCT['House Committee on Appropriations:HSAP'] = [20]
    dCT['House Committee on Armed Services:HSAS'] = [16]
    dCT['House Committee on Committees:HLCQ'] = []
    dCT['House Committee on District of Columbia:HSDT'] = []
    dCT['House Committee on Education and Labor:HSED'] = [6,5]
    dCT['House Committee on 8 (Ad Hoc):HHAH'] = [8]
    dCT['House Committee on 8 and Commerce:HSIF'] = [8]
    dCT['House Committee on Ethics:HSSO'] = []
    dCT['House Committee on Ethics (Select):HLET'] = []
    dCT['House Committee on Financial Services:HSBA'] = [15,1]
    dCT['House Committee on Foreign Affairs:HSFA'] = [18,19]
    dCT['House Committee on Homeland Security:HSHM'] = [19,5]
    dCT['House Committee on House Administration:HSHA'] = []
    dCT['House Committee on Internal Security:HSUA'] = []
    dCT['House Committee on Joint Atomic 8:HSAT'] = [8]
    dCT['House Committee on Merchant Marine and Fisheries:HSMM'] = [7]
    dCT['House Committee on Natural Resources:HSII'] = [7,21,8]
    dCT['House Committee on Outer Continental Shelf (Select):HLOC'] = []
    dCT['House Committee on Oversight and Government Reform:HSGO'] = [20]
    dCT['House Committee on Post Office and Civil Service:HSPO'] = [20]
    dCT['House Committee on Rules:HSRU'] = [20]
    dCT['House Committee on Science and Technology:HSSY'] = [17]
    dCT['House Committee on Small Business:HSSM'] = [10]
    dCT['House Committee on Standards of Official Conduct:HSSO'] = [20]
    dCT['House Committee on Temporary Joint Committee on Deficit Reduction:HTDE'] = [20]
    dCT['House Committee on Transportation and Infrastructure:HSPW'] = [10]
    dCT['House Committee on Veterans\' Affairs:HSVR'] = [16]
    dCT['House Committee on Ways and Means:HSWM'] = [1]
    dCT['House Committee on the Budget:HSBU'] = [20]
    dCT['House Committee on the Judiciary:HSJU'] = [12]
    dCT['House Permanent Select Committee on Intelligence:HLIG'] = [16,19]
    dCT['House Select Committee on 8 Independence and Global Warming:HSGW'] = [8,7]
    dCT['Joint Committee on Printing:JSPR'] = []
    dCT['Joint Committee on Taxation:JSTX'] = [1]
    dCT['Joint Committee on the Library:JSLC'] = []
    dCT['Joint Economic Committee:JSEC'] = [1,15]
    dCT['Senate Commission on Security and Cooperation in Europe:HCSE'] = [19]
    dCT['Senate Committee on Aeronautical and Space Sciences:SSAE'] = [17]
    dCT['Senate Committee on Agriculture, Nutrition, and Forestry:SSAF'] = [4,7,21]
    dCT['Senate Committee on Appropriations:SSAP']= [20]
    dCT['Senate Committee on Armed Services:SSAS'] = [16]
    dCT['Senate Committee on Banking, Housing, and Urban Affairs:SSBK'] = [15,14]
    dCT['Senate Committee on Commerce, Science, and Transportation:SSCM'] = [10,17,15]
    dCT['Senate Committee on District of Columbia:SSDT'] = []
    dCT['Senate Committee on 8 and Natural Resources:SSEG'] = [8,21]
    dCT['Senate Committee on Environment and Public Works:SSEV'] = [7,21]
    dCT['Senate Committee on Finance:SSFI'] = [15]
    dCT['Senate Committee on Foreign Relations:SSFR'] = [19]
    dCT['Senate Committee on Health, Education, Labor, and Pensions:SSHR'] = [3,6,5]
    dCT['Senate Committee on Homeland Security and Governmental Affairs:SSGA'] = [16]
    dCT['Senate Committee on Impeachment (Special) (Hastings):SPIM'] = []
    dCT['Senate Committee on Indian Affairs:SLIA'] = [21]
    dCT['Senate Committee on Official Conduct (Special):SPOC'] =  [20]
    dCT['Senate Committee on POW/MIA Affairs:SLPO'] = [16]
    dCT['Senate Committee on Post Office and Civil Service:SSPO'] =  [20]
    dCT['Senate Committee on Rules and Administration:SSRA'] =  [20]
    dCT['Senate Committee on Small Business and Entrepreneurship:SSSB'] = [15]
    dCT['Senate Committee on Veterans\' Affairs:SSVA'] = [16]
    dCT['Senate Committee on Whitewater Dev Corp Investigation (Special):SPWW']=[20]
    dCT['Senate Committee on the Budget:SSBU'] =  [20]
    dCT['Senate Committee on the Judiciary:SSJU'] = [12]
    dCT['Senate Select Committee on Ethics:SLET'] = [20]
    dCT['Senate Select Committee on Intelligence:SLIN'] = [16,19]
    dCT['Senate Special Committee on Aging:SPAG'] = [3]
    dCT['United States Senate Caucus on International Narcotics Control:SCNC'] = [12]
    
    for fullName,topics in dCT.items():
        print fullName
        code = fullName.split(':')[1]
        commObjs = Committee.objects.filter(code=code)
        for co in commObjs:
            co.topics = []
            co.save()
            for t in topics:
                topic = JonesTopic.objects.filter(code=t)[0]
                co.topics.add(topic)
                
        print co.topics.all()
        co.save()
            #co.save()

def loadCommittees(congressNum):
    start = datetime.datetime.now()
    xml = pyU._getFile('http://www.govtrack.us/data/us/%d/committees.xml' % congressNum)

    congressObj = Congress.objects.get(number=congressNum)
    doc = BeautifulSoup(xml)
    
    end = datetime.datetime.now()
    delta = end-start
    print delta.seconds
    print delta.microseconds
    for comm in doc.findAll('committee'):
        start = datetime.datetime.now()
        reps = []
        
        typeComm = None
        if comm['type'] == 'senate': typeComm='SENATE'
        elif comm['type'] == 'house': typeComm = 'HOUSE'
        elif comm['type'] == 'joint':typeComm='JOINT'
        
        
        name = comm['displayname']
        print name
        code = comm['code']
        try:
            chair = Rep.objects.get(repGovTrackID=comm.find('member',{'role':re.compile('Chair.*')})['id'],congress=congressObj)
        except Exception:
            chair=None
        
        try:
            vChair = Rep.objects.get(repGovTrackID=comm.find('member',{'role':'Vice Chairman'})['id'],congress=congressObj)
        except Exception:
            vChair=None
        
        try:
            rm = Rep.objects.get(repGovTrackID=comm.find('member',{'role':re.compile('Ranking.*')})['id'],congress=congressObj)
        except Exception:
            rm = None
        
        
        for rep in comm.findAll('member'):
            try:
                reps.append(Rep.objects.get(repGovTrackID=rep['id'],congress=congressObj))
            except Exception,ex:
                print 'WHY NO REP FOR %s' % rep
                continue
        try:
           committee = Committee.objects.get_or_create(typeComm=typeComm,code=code,name=name,congress=congressObj,chair=chair,rankingMember=rm,viceChair=vChair)[0]
           for rep in reps:
               committee.reps.add(rep)
           end = datetime.datetime.now()
           delta = end-start
           #print delta.seconds
           #print delta.microseconds
           committee.save()
        except Exception:
           pass
        #assert 0
        
if __name__ == '__main__':
    #Committee.objects.all().delete()
    loadCommittees(112)
    #loadCommittees(111)
    #mapCommitteesToTopics()
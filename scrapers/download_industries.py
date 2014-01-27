import pyUtilities as pyU
from BeautifulSoup import BeautifulSoup
from ccu_gen_beta.models import *
from datetime import date
import time
from paths import *
import datetime

def getHTMLTwiceNAICS(url):

    for i in range(0,3):
        html = pyU._getFile(url)
        doc = BeautifulSoup(html)
        table = doc.find('table',{'class':'lehd'})
        if table:
            return doc
        time.sleep(2.0)

    return None


naics_dir = {}
naics_indir = {}
def makenaicsDictionary():
    global naics
    txt = open(CCU_DATA_PATH + 'naics_to_crp.txt').read()
    lines = txt.split('\n')
    for line in lines[1:]:
        line2 = line
        #industry_name = line2.split('\t')[1]
        naics_code = pyU.toascii(line2.split('\t')[-1]).replace('\r','')
        crp_code = pyU.toascii(line2.split('\t')[0])
        naics_dir[naics_code] = [crp_code]
    
    #some are not defined, do this here...
    #Credit intermediation and related activities: credit agencies & finance, credit unions
    naics_indir['522'] = ['F1300','F1400']
    
    #Professional, Scientific, Technical Services
    #NOT DOING TOO BROAD...
    
    #General merchandise stores
    naics_indir['452'] = ['G4300']
    
    #Transportation Equipment Manufacturing --> Auto manufacturers, Truck & Trailer manufacturers, Aircract manufacturers
    naics_indir['336'] = ['T2100','T3200','T1200']

    #??Support activities for mining --> mining services & equipment, oilfield service, equipment & exploration
    naics_indir['213'] = ['E1240','E1150']
    
    #Merchant wholesalers
    #NOT DOING TOO BROAD...
    
    #Education services --> Technical, business & vocationals schools, schools & colleges, public school, medical school, law school
    naics_indir['611'] = ['H5200','H5100','X3500','H5150','H5170']
    
    #Accomodation --> Hotels & motels, resorts
    naics_indir['721'] = ['T9100','T9300']
    
    #??Heavy and Civil Engineering Construction-->oilfield service, equipment & exploration
    naics_indir['237'] = ['E1150']
    
    #Insurance carriers --> Accident & Health insur, Insurance, Insurance companies, brokers, Life insurance, Property & casualty insur, Finance--insurance & real estate
    naics_indir['524'] = ['F3200','F3000','F3100','F3300','F3400','F0000']
    
    #Management of Companies and Enterprises --> Commercial banks & bank holding companies
    naics_indir['551'] = ['F1100']

def createNAICSIndustry(naicsCode,name):
    naicsObj = NAICS_Industry()
    naicsObj.name=name
    naicsObj.code=naicsCode
    if naicsCode in naics_dir: 
        naicsObj.mlDirectMapping=True
        naicsObj.mlBusinesses = MapLightBusiness.objects.filter(mlID__in=naics_dir[naicsCode])
    elif naicsCode in naics_indir: 
        naicsObj.mlDirectMapping=False
        naicsObj.mlBusinesses = MapLightBusiness.objects.filter(mlID__in=naics_indir[naicsCode])
    naicsObj.save()
    return naicsObj
        
def getStateIndustries():
    dName = {}
    global naics
    #makenaicsDictionary()
    #print naics

    start = False
    for state in State.objects.all():
        start = datetime.datetime.now()
        print "*******************************"
        print state
        print "********************************"
        #for 2009-2010
        #url = 'http://lehd.did.census.gov/cgi-bin/broker?_SERVICE=industry_focus&_PROGRAM=pgm.top_report.sas&_table=no&_skin=0&_from=pgm.top_report.sas&_top=10&_rankings=1+&_1=ON&_agegroup=A00+&_sex=0+&_state=%s+&_entity=state&_level=naics3&_Ind2=off&_pgmrun=View+Report'
       
        #for 2011-2012
        url = 'http://lehd.did.census.gov/cgi-bin/broker?_SERVICE=industry_focus&_PROGRAM=pgm.top_report.sas&_table=no&_skin=0&_from=pgm.top_report.sas&_top=10&_rankings=1+&_1=ON&_entity=state&_state=%s&_geog=000&_ind2=off&_ind3=000&_level=naics3&_agegroup=A00+&_sex=0+&_pgmrun=View+Report'
        
        url = url % state.abbrev.lower()
       
        doc = getHTMLTwiceNAICS(url)
        if not doc:
            continue
        table = doc.find('table',{'class':'lehd'})
        head_row = doc.findAll('th',{'class':'header'})[-1]
        quarters = head_row.findAll(text=True)
        print quarters
        assert 0

        begin_quarter = int(quarters[-2].split(',')[0].split('Q')[1].replace('(',''))
        begin_year = int(quarters[-2].split(',')[0].split('Q')[0].replace('(',''))
        end_quarter = int(quarters[-1].split(',')[-1].split('Q')[1].replace(')',''))
        end_year = int(quarters[-1].split(',')[-1].split('Q')[0])
        print end_year
        #continue
        rows = table.findAll('tr')
        state_pop = int(rows[1].findAll('td')[2].string.replace(",",""))
                
        finalRet = {}
        for row in rows[2:]:
           
            cols = row.findAll('td',{'class':'r Data'})
            name = cols[0].find('a').string
            
            code = name.split()[0]
            name = ' '.join(name.split()[1:])
            emps = int(pyU.removePunctuation(cols[1].string))
            naicsLoc = NAICS_Locale2()
            naicsLoc.state = state
            naicsLoc.beginQuarter = begin_quarter
            naicsLoc.beginYear = begin_year
            naicsLoc.endQuarter = end_quarter
            naicsLoc.endYear = end_year
            naicsLoc.numEmployees = emps
            naicsLoc.numEmployeesTotal = state_pop
            
            # print ""
            #  print name
            #  print 'naics ' + code
            #  print "-------------------------"
            if NAICS_Industry.objects.filter(code=int(code)).count() == 0:
                naicsIndObj = createNAICSIndustry(code,name)
            else:
                naicsIndObj = NAICS_Industry.objects.get(code=int(code))
              
            naicsLoc.naicsIndustry = naicsIndObj
            try:
               naicsLoc.save()
               #end = datetime.datetime.now()
               #delta = end-start
               #print delta.seconds
               #print delta.microseconds
               #assert 0
            except Exception,ex:
               print ex
               #pass
        
            
            #print naicsLoc
            #assert 0

if __name__ == '__main__':
    #NAICS_Locale.objects.all().delete()
    #NAICS_Industry.objects.all().delete()
    getStateIndustries()
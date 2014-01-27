from ccu_gen_beta.models import * 

def mapJonesNAICS(naicsName):
    
    if naicsName=="Private Households":
        return []
    
    if naicsName=="Food Services and Drinking Places":
        return ['Food inspection']
    
    if naicsName=="Accommodation":
        return ['tourism']
    
    if naicsName=="Amusement, Gambling, and Recreation Industries":
        return ['tourism','native american affairs']
    
    if naicsName=="Social Assistance":
        return ['social services','elderly issues','poverty and assistance','unemployment rate','food stamps', 'infants and children']
    
    if naicsName=="Nursing and Residential Care Facilities":
        return ['long-term care']
    
    if naicsName=="Hospitals":
        return ['facilities construction','comprehensive health','insurance reform']
    
    if naicsName=="Ambulatory Health Care Services":
        return []
    
    if naicsName=="Educational Services":
        return ['higher education','elementary','education of underprivil','vocational','special','educational excellence']
    
    if naicsName=="Administrative and Support Services":
        return []
    
    if naicsName=="Management of Companies and Enterprises":
        return ['securities','consumer finance']
    
    if naicsName=="Professional, Scientific, and Technical Services":
        return ['securities','consumer finance','Telephone','Broadcast','Computer']
    
    if naicsName=="Insurance Carriers and Related Activities":
        return ['U.S. banking','insurance regulation','secondary mortgage','provider and insurer payment','employee benefits','consumer safety']
    
    if naicsName=="Credit Intermediation and Related Activities":
        return ['U.S. Banking','Consumer Finance','Small Business','Secondary Mortgage','Monetary Supply','consumer safety']
    
    if naicsName=="Publishing Industries (except Internet)":
        return []
    
    if naicsName=="Truck Transportation":
        return ['truck and automobile']
    
    if naicsName=="General Merchandise Stores":
        return ['tariff and import']
    
    if naicsName=="Food and Beverage Stores":
        return ['tariff and import','food inspection']
    
    if naicsName=="Merchant Wholesalers, Nondurable Goods":
        return ['agricultural trade','export promotion']
    
    if naicsName=="Merchant Wholesalers, Durable Goods":
        return ['export promotion']
        
    if naicsName=="Transportation Equipment Manufacturing":
        return ['Truck and Automobile Transportation and Safety','Productivity and Competitiveness of U.S. Business, U.S. Balance of Payments']
    
    if naicsName=="Computer and Electronic Product Manufacturing":
        return ['Computer Industry and Computer Security']
    
    if naicsName=="Fabricated Metal Product Manufacturing":
        return ['Worker Safety and Protection, Occupational and Safety Health Administration (OSHA)']
    
    if naicsName=="Food Manufacturing":
        return ['Food inspection']
    
    if naicsName=="Specialty Trade Contractors":
        return ['tariff and import','export promotion']
    
    if naicsName=="Heavy and Civil Engineering Construction":
        return ['Facilities construction, regulation, and payments','Worker Safety and Protection, Occupational and Safety Health Administration (OSHA)','highway construction']
    
    if naicsName=="Support Activities for Mining":
        return ['Natural Resources, Public Lands, and Forest Management','Coal','Worker Safety']
    
    if naicsName=="Mining (except Oil and Gas)":
        return ['Natural Resources, Public Lands, and Forest Management','Coal','Worker Safety']

def mapAllJonesNAICS():
    for ind in NAICS_Industry.objects.all():
        ind.subtopics=[]
        ind.save()
    
    
    for ind in NAICS_Industry.objects.all():
        #print ind.name
        ret = mapJonesNAICS(ind.name)
        for stName in ret:
            try:
                st = JonesSubTopic.objects.get(name__istartswith=stName)
                
                #print st
                #print ind.subtopics.all()
                if ind.subtopics.all().count() > 0:
                    lsST = list(ind.subtopics.all())
                else:
                    lsST = []
                lsST.append(st)
                #print lsST
                ind.subtopics = lsST
                ind.save()
            except Exception,ex:
                print ex
                #assert 0
                #print "SUBTOPIC: %s not matched" % stName

if __name__ == '__main__':
    mapAllJonesNAICS()
    for ind in NAICS_Industry.objects.all():
        print ind.name
        print ind.subtopics.all()
        print ""   
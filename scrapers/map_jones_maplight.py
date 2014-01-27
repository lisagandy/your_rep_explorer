from ccu_gen_beta.models import *

def mapJonesTopicToMaplightSector(jsName):
    #sector to topics
    d = {}
    d['Transportation'] = ['Transportation']
    d['Misc'] = ['Macroeconomics','Banking']
    d['Lawyers'] = ['Law']
    d['Labor'] = ['Labor']
    d['Ideology'] = ['Social','Civil']
    d['Health'] = ['Health','Banking']
    d['Finance/Insurance'] = ['Macro','Banking','Health']
    d['Energy/Natural'] = ['Energy']
    d['Education'] = ['Education']
    d['Defense'] = ['Defense']
    d['Construction'] = ['Public','Labor']
    d['Communicationsic/Elect'] = ['Space'] #TODO: FIX LATER
    d['Agribusiness'] = ['Agriculture']


def mapJonesSubToMaplightBusiness(jsName,jsTopicName):
    #------AGRICULTURE--------------------#
    
    if jsName=="General" and jsTopicName == "Agriculture":
        return ['Agricultural Services','Farm Bureaus','Farm organizations']
    
    if jsName=="Agricultural Trade":
         return ['tobacco','Agricultural Services','Farm Machinery','Farm organization','Grain traders','Farm bureaus','milk & dairy','sugar cane','vegetables','other commodities','cotton','wheat','farmers, crop','milk','livestock','feedlots','sheep']

    if jsName=="Government Subsidies to Farmers and Ranchers, Agricultural Disaster Insurance":
         return ['Farm organization','Farm Bureaus','crop production','sugar cane','vegetables','other commodities','cotton','wheat','farmers']

    if jsName=="Food Inspection and Safety (including seafood)":
         return ['Grain Traders','Meat processing','Agriculture','food and kindred products manufact','meat processing','beverage','food & beverage','poultry']

    if jsName=="Agricultural Marketing, Research, and Promotion":
         return ['milk & dairy','sugar cane','vegetables','other commodities','cotton','wheat','farmers, crop','milk','livestock','feedlots','sheep','tobacco']

    if jsName=="Animal and Crop Disease and Pest Control":
         return ['Agricultural Chemicals']

    if jsName=="Agricultural Research and Development":
         return ['Agricultural Chemicals','Agricultural Services','animal feed & health products']
    
    #-------------
         
    #-----------FINANCE-------------------#
    if jsName=="General" and jsTopicName.find('anking') > -1:
         return [] 

    if jsName=="U.S. Banking System and Financial Institution Regulation":
         return ['Commercial Banks','Banks &','Savings Banks','Finance,','Financial','Commodity','Mortgage','Securities']

    if jsName=="Securities and Commodities Regulation":
         return ['Securities','Security brokers','Commodity']

    if jsName=="Consumer Finance, Mortgages, and Credit Cards":
         return ['Mortgage','Finance, Insurance','Financial','Credit agencies','Credit Unions','Commercial banks','Banks &','hmo']

    if jsName=="Insurance Regulation":
         return ['Accident & Health','Insurance companies','Finance, Insurance','hmo']

    if jsName=="Bankruptcy":
         return ['Banks &','Commercial Banks','Credit agencies']

    if jsName=="Corporate Mergers, Antitrust Regulation, and Corporate Management Issues":
         return ['Banks &','Commercial Banks','Credit Agencies','Savings Banks','Financial services','Investors','Securities','Security brokers']

    if jsName=="Small Business Issues and the Small Business Administration":
         return ['Small business assoc','Pro-business assoc','General business assoc','Chambers of commerce','Business tax']

    if jsName=="Copyrights and Patents":
         return ['Venture capital']
         
    if jsName=="Domestic Disaster Relief":
         return []
    
    if jsName=="Tourism":
         return ['lodging','hotels','travel','resort','cruise ships']
    
    if jsName=="Consumer Safety and Consumer Fraud":
         return ['consumer groups','direct mail advert','toiletries','funeral','credit reporting services & collection agencies','auto repair','Banks','Commercial banks','Credit agencies','Payday lenders','Insurance companies','Life insurance','Property & casualty','Financial services','Investors','Real estate','Commodity','Hedge','Investment','Private Equity','Securities','Security']

    if jsName=="Sports and Gambling Regulation":
         return ['professional sports','indian gaming','casinos']
    
    if jsName=="Other" and jsTopicName.find('anking') > -1:
         return []
    #--------------#

    #-----------CIVIL RIGHTS-------------------#
    if jsName=="General" and jsTopicName.find('ivil') > -1:
        return ['minority']

    if jsName=="Ethnic Minority and Racial Group Discrimination":
         return ['minority','welfare','human']

    if jsName=="Gender and Sexual Orientation Discrimination":
         return ['minority','gay','human','women']

    if jsName=="Age Discrimination":
         return ['minority','human']

    if jsName=="Handicap or Disease Discrimination":
         return ['minority','welfare','human']

    if jsName=="Voting Rights and Issues":
         return ['human rights']

    if jsName=="Freedom of Speech & Religion":
         return ['gay','human rights']

    if jsName=="Right to Privacy and Access to Government Information":
         return []

    if jsName=="Anti-Government Activities":
         return ['militias']
    
    if jsName=="Other" and jsTopicName.find('ivil') > -1:
         return []

    #---------------------#     
    #-----------COMMUNITY DEVELOPMENT-------------------#


    if jsName=="Housing and Community Development":
         return []
    
    if jsName=="Urban Economic Development and General Urban Issues":
        return []

    if jsName=="Rural Economic Development":
         return ['welfare']

    if jsName=="Low and Middle Income Housing Programs and Needs":
         return ['minority','welfare']

    if jsName=="Veterans Housing Assistance and Military Housing Programs":
         return []

    if jsName=="Elderly and Handicapped Housing":
         return ['minority']

    if jsName=="Housing Assistance for Homeless and Homeless Issues":
         return []

    if jsName=="Secondary Mortgage Market":
         return ['mortgage']

    #-----------------------------#
    
    #-----------DEFENSE-------------------#
    if jsName=="General" and jsTopicName.find('efense') > -1:
         return []
    
    if jsName=="U.S. and Other Defense Alliances, U.S Security Assistance":
         return []
    
    if jsName=="Military Intelligence, CIA, Espionage":
         return []
         
    if jsName=="Military Aid and Weapons Sales to other Countries":
         return ['defense aerospace','defense electronic','defense-related services','ground-based','import/export']

    if jsName=="Military Readiness, Coordination of Armed Services Air Support and Sealift Capabilities, and National Stockpiles of Strategic Materials":
         return ['defense aerospace','defense electronic','defense-related services','ground-based','defenseSTOP']

    if jsName=="Arms Control and Nuclear Nonproliferation":
         return ['defense aerospace','defense electronic','defense-related services','ground-based','defenseSTOP','defense policy']

    if jsName=="Manpower, Military Personnel and Dependents (Army, Navy, Air Force, Marines), Military Courts":
         return ['defenseSTOP']

    if jsName=="VA Issues":
         return []

    if jsName=="Military Procurement and Weapons System Acquisitions and Evaluation":
         return ['defense aerospace','defense electronic','defense-related services','ground-based']

    if jsName=="Military Installations, Construction, and Land Transfers":
         return ['defenseSTOP']

    if jsName=="National Guard and Reserve Affairs":
         return ['defenseSTOP']

    if jsName=="Military Nuclear and Hazardous Waste Disposal, Military Environmental Compliance":
         return ['waste management','defenseSTOP']

    if jsName=="Civil Defense (war related)":
         return ['foreign policy','defense policy','defense aerospace','defense electronic','defense-related services','defenseSTOP']

    if jsName=="DOD Civilian Personnel, Civilian Employment by the Defense Industry, Military Base Closings":
         return ['defenseSTOP']

    if jsName=="Oversight of Defense Contracts and Contractors":
         return ['defense aerospace','defense electronic','defense-related','homeland security','defenseSTOP']

    if jsName=="Direct War Related Issues":
         return ['defenseSTOP']

    if jsName=="Relief of Claims Against U.S. Military:":
         return []
         
    if jsName=="Research and Development" and jsTopicName.find('efense') > -1:
         return ['defense aerospace','defense electronic','defense-related services','ground-based','defenseSTOP']
    
    if jsName=="Other" and jsTopicName.find('efense') > -1:
         return []    
         
    #---------------EDUCATION-------------#     
    if jsName=="General" and jsTopicName.find('ducation')>-1:
         return []     
         
    if jsName=="Higher Education":
         return ['schools & colleges','law schools','for-profit education','medical schools','education']

    if jsName=="Elementary and Secondary Education":
         return ['schools & colleges','education']

    if jsName=="Education of Underprivileged Students":
         return ['schools & colleges','welfare','education']

    if jsName=="Vocational Education":
         return ['technical, business','education']

    if jsName=="Special Education":
         return ['schools & colleges','education']

    if jsName=="Educational Excellence":
         return ['schools & colleges','education']

    if jsName=="Arts and Humanities":
         return []

    if jsName=="Research and Development" and jsTopicName.find('ducation') > -1:
         return ['education']
         
    if jsName=="Other" and jsTopicName.find('ducation') > -1:
         return ['schools & colleges','education']     
         
    #--------------ENERGY----------------#     
         
    if jsName=="Nuclear Energy and Nuclear Regulatory Commission Issues":
         return ['nuclear energy','nuclear plant','energy production']

    if jsName=="Electricity and Hydroelectricity":
         return ['energy production','gas & electric','electric power','electric power utilities','rural electric','independent','nuclear energy','nuclear plant','water utilities','power plant']

    if jsName=="Natural Gas and Oil (Including Offshore Oil and Gas)":
         return ['petroleum refining','gas & electric','major (multinational) oil & gas producers','independent oil','oil & gas','oilfield service','natural gas transmission','gasoline service','LPG','fuel oil']

    if jsName=="Coal":
         return ['coal mining','mining','mining services']

    if jsName=="Alternative and Renewable Energy":
         return ['energy production','alternate energy','electric power','electric power utilities']

    if jsName=="Energy Conservation":
         return ['energy, natural resources and environment','alternative']

    if jsName=="Research and Development" and jsTopicName.find('nergy') > -1:
         return []
         
    #--------------------#     
    
    #----------ENVIRONMENT----------------#
         
    if jsName=="Drinking Water Safety":
         return []

    if jsName=="Waste Disposal":
         return ['waste management']

    if jsName=="Hazardous Waste and Toxic Chemical Regulation, Treatment, and Disposal":
         return ['waste management']

    if jsName=="Air pollution, Global Warming, and Noise Pollution":
         return ['electric power utilities','environmental policy']

    if jsName=="Recycling":
         return ['recycling of metal']

    if jsName=="Indoor Environmental Hazards":
         return ['environmental policy']

    if jsName=="Species and Forest Protection":
         return ['hunting','fisheries & wildlife']

    if jsName=="Coastal Water Pollution and Conservation":
         return ['fishing','environmental policy']

    if jsName=="Land and Water Conservation":
         return ['coal mining','mining','metal mining','mining services','non-metallic mining','environmental policy']

    if jsName=="Research and Development" and jsTopicName.find('nvironment') > -1:
         return []

    #---------------#
    #-----------------FOREIGN TRADE----------------#
    
    if jsName=="Trade Negotiations, Disputes, and Agreements":
         return ['international trade associations','import/export']

    if jsName=="Export Promotion and Regulation, Export-Import Bank":
         return ['import/export']

    if jsName=="International Private Business Investments, Overseas Private Investment Corporation (OPIC)":
         return ['investment banking','investors','private equity','securities']

    if jsName=="Productivity and Competitiveness of U.S. Business, U.S. Balance of Payments":
         return []

    if jsName=="Tariff and Import Restrictions, Import Regulation":
         return ['international trade associations','import/export']

    if jsName=="Exchange Rates and Related Issues":
         return ['international trade associations','import/export']
    #--------------#
    

    if jsName=="Intergovernmental Relations":
         return []

    if jsName=="Government Efficiency and Bureaucratic Oversight":
         return []

    if jsName=="Postal Service Issues (Including Mail Fraud)":
         return ['US Postal Service unions','US Postal ServiceSTOP']

    if jsName=="Government Employee Benefits, Civil Service Issues":
         return ['civil servant','civil service & government unions']

    if jsName=="Nominations and Appointments":
         return ['public official']

    if jsName=="Currency, Commemorative Coins, Medals, U.S. Mint":
         return []

    if jsName=="Government Procurement, Procurement Fraud and Contractor Management":
         return []

    if jsName=="Government Property Management":
         return []

    if jsName=="IRS Administration":
         return ['fiscal & tax','tax return']

    if jsName=="Presidential Impeachment & Scandal":
         return []

    if jsName=="Federal Government Branch Relations and Administrative Issues, Congressional Operations":
         return []

    if jsName=="Regulation of Political Campaigns, Political Advertising, PAC regulation, Voter Registration, Government Ethics":
         return []

    if jsName=="Census":
         return []

    if jsName=="District of Columbia Affairs":
         return []

    if jsName=="Relief of Claims Against the U.S. Government":
         return []

    if jsName=="Federal Holidays":
         return []



    #--------------HEALTH--------------------------------#
    if jsName=="Comprehensive health care reform":
         return ['Health Professionals','Hospitals','Pharma','HMOS','physicians','nurse','health care services']

    if jsName=="Insurance reform, availability, and cost":
         return ['Accident & health','insurance','insurance companies','physicians','hmos']

    if jsName=="Regulation of drug industry, medical devices, and clinical labs":
         return ['Pharma','medical laboratories']

    if jsName=="Facilities construction, regulation, and payments":
         return ['health care institutions','hospitals','nursing homes']

    if jsName=="Provider and insurer payment and regulation":
         return ['Accident & health','insurance','physicians','hmos','health care services']

    if jsName=="Medical liability, fraud and abuse":
         return ['Hospitals','Accident & health','insurance','physicians','health care services']

    if jsName=="Health Manpower & Training":
         return ['Health profess','physicians','nurse']

    if jsName=="Prevention, communicable diseases and health promotion":
         return ['Health, Education','AIDS treatment']

    if jsName=="Infants and children":
         return ['Health, Education','Health & welfare','childrens rights']

    if jsName=="Mental illness and mental retardation":
         return ['mental health','psy']

    if jsName=="Long-term care, home health, terminally ill, and rehabilitation services":
         return ['Home care services','Nursing homes','health care services']

    if jsName=="Prescription drug coverage and costs":
         return(['Pharma','Accident & health','insurance'])

    if jsName=="Tobacco Abuse, Treatment, and Education":
         return ['Health, educ','tobacco']

    if jsName=="Alcohol Abuse and Treatment":
         return ['Outpatient health','Drug &','psy','alcoholSTOP']

    if jsName=="Illegal Drug Abuse, Treatment, and Education":
         return ['Outpatient health','Drug &','psy']

    if jsName=="Drug and Alcohol or Substance Abuse Treatment":
         return ['Outpatient health','Drug &','psy']

    if jsName=="Research and development":
         return ['Medical lab','Biotech products']

    #--------------#     
    
    #----------INTERNATIONAL AFFAIRS--------------#

    if jsName=="U.S. Foreign Aid":
         return []

    if jsName=="International Resources Exploitation and Resources Agreement":
         return []

    if jsName=="Developing Countries Issues (for financial issues see 1906)":
         return []

    if jsName=="International Finance and Economic Development":
         return ['international trade associations','import/export']

    if jsName=="China":
         return []

    if jsName=="Soviet Union and Former Republics":
         return []

    if jsName=="Eastern Europe":
         return []

    if jsName=="Western Europe, Common Market Issues":
         return []

    if jsName=="Africa":
         return []

    if jsName=="South Africa":
         return []

    if jsName=="Latin America (South America, Central America, Mexico, Caribbean Basin, Cuba)":
         return []

    if jsName=="Panama Canal Issues and Other International Canal Issues":
         return []
    
    if jsName=="Asia, Pacific Rim, Australia, and Japan":
         return []

    if jsName=="Middle East":
         return ['pro-arab','pro-israel']

    if jsName=="Human Rights":
         return ['human rights']

    if jsName=="International Organizations other than Finance: United Nations (UN), UNESCO, International Red Cross":
         return []

    if jsName=="Terrorism, Hijacking":
         return []

    if jsName=="U.S. Diplomats, U.S. Embassies, U.S. Citizens Abroad, Foreign Diplomats in the U.S., Passports":
         return []
         
    #-------------------#     
         
    #--------------LABOR----------------#     

    if jsName=="Worker Safety and Protection, Occupational and Safety Health Administration (OSHA)":
         return []

    if jsName=="Employment Training and Workforce Development":
         return []

    if jsName=="Employee Benefits":
         return ['insurance companies','life insurance','accident & health','insuranceSTOP','finance, insurance']

    if jsName=="Employee Relations and Labor Unions":
         return ['labor, anti-union','building trades unions','food service & related unions','commercial service unions','general commercial unions','labor unions','entertainment unions','other unions','retail trade unions','health worker unions','agricultural labor','defense-related unions','other commercial','manufacturing unions','IBEW','communications & hi-tech unions','automotive unions','defense-related unions','mining unions','energy-related unions','us postal service unions','teachers unions','federal employees unions','police & firefighters unions','state & local govt employee unions','civil service & government unions','air transport unions','merchant marine & longshoremen unions','transportation unions','teamsters union','other transportation unions','railroad unions','automotive unions']

    if jsName=="Fair Labor Standards":
         return ['labor, anti-union','building trades unions','food service & related unions','commercial service unions','general commercial unions','labor unions','entertainment unions','other unions','retail trade unions','health worker unions','agricultural labor','defense-related unions','other commercial','manufacturing unions','IBEW','communications & hi-tech unions','automotive unions','defense-related unions','mining unions','energy-related unions','us postal service unions','teachers unions','federal employees unions','police & firefighters unions','state & local govt employee unions','civil service & government unions','air transport unions','merchant marine & longshoremen unions','transportation unions','teamsters union','other transportation unions','railroad unions','automotive unions']

    if jsName=="Youth Employment, Youth Job Corps Programs, and Child Labor":
         return []

    if jsName=="Parental Leave and Child Care":
         return []

    if jsName=="Migrant and Seasonal workers, Farm Labor Issues":
         return ['agricultural labor unions','immigration rights','border control']

    if jsName=="Immigration and Refugee Issues":
         return ['immigration rights','border control']
    #---------------#
    
    #--------------LAW, CRIME AND FAMILY ISSUES------------#

    if jsName=="Executive Branch Agencies Dealing With Law and Crime":
         return []

    if jsName=="White Collar Crime and Organized Crime":
         return []

    if jsName=="Illegal Drug Production, Trafficking, and Control":
         return []

    if jsName=="Court Administration":
         return []

    if jsName=="Prisons":
         return []

    if jsName=="Juvenile Crime and the Juvenile Justice System":
         return []

    if jsName=="Child Abuse and Child Pornography":
         return []

    if jsName=="Family Issues":
         return []

    if jsName=="Police, Fire, and Weapons Control":
         return ['anti-guns','pro-guns']

    if jsName=="Criminal and Civil Code":
         return []

    if jsName=="Riots and Crime Prevention":
         return ['anti-guns','pro-guns']

    #--------MACROECONOMICS---------------------#

    if jsName=="Inflation, Prices, and Interest Rates":
         return ['banks &','commercial banks','savings banks']

    if jsName=="Unemployment Rate":
         return []

    if jsName=="Monetary Supply, Federal Reserve Board, and the Treasury":
         return []

    if jsName=="National Budget and Debt":
         return []

    if jsName=="Taxation, Tax policy, and Tax Reform":
         return ['real estate','security brokers','investment','stock','investors','insurance','commercial banks']

    if jsName=="Industrial Policy":
         return []

    if jsName=="Price Control and Stabilization":
         return []
         
    #----------------------#     
    
    #---------PUBLIC LANDS AND WATER MANAGEMENT---------------#     

    if jsName=="National Parks, Memorials, Historic Sites, and Recreation":
         return []

    if jsName=="Native American Affairs":
         return ['indian gaming']

    if jsName=="Natural Resources, Public Lands, and Forest Management":
         return ['energy, natural resources and environment']

    if jsName=="Water Resources Development and Research":
         return []

    if jsName=="U.S. Dependencies and Territorial Issues":
         return []


    #----------------SOCIAL WELFARE------------------#

    if jsName=="Food Stamps, Food Assistance, and Nutrition Monitoring Programs":
         return []

    if jsName=="Poverty and Assistance for Low-Income Families":
         return []

    if jsName=="Elderly Issues and Elderly Assistance Programs (Including Social Security Administration)":
         return ['elderly issues']

    if jsName=="Assistance to the Disabled and Handicapped":
         return ['home care services']

    if jsName=="Social Services and Volunteer Associations":
         return []

    #--------------------#

    #-----------------------SPACE, SCIENCE, TECH...-------------------#

    if jsName=="NASA, U.S. Government Use of Space, Space Exploration Agreements":
         return ['defense aerospace']

    if jsName=="Commercial Use of Space, Satellites":
         return ['defense aerospace','space vehicles','satellite']

    if jsName=="Science Technology Transfer, International Scientific Cooperation":
         return []

    if jsName=="Telephone and Telecommunication Regulation":
         return ['telephone utilities','communications & electronics','cellular','telecomm','telephone &','long-distance telephone']

    if jsName=="Broadcast Industry Regulation (TV, Cable, Radio)":
         return ['cable & satellite','commercial TV']

    if jsName=="Weather Forecasting and Related Issues, NOAA, Oceanography":
         return []

    if jsName=="Computer Industry and Computer Security":
         return ['computer software','online computer services','computers, components','computer manufacture','data processing']

    if jsName=="Research and Development" and jsTopicName.find('Communic') > -1:
         return ['higher education','school & colleges','for-profit']

    #---------------#

    #----------TRANSPORTATION-------------#

    if jsName=="Mass Transportation and Safety":
         return ['bus services','taxicabs','buses & taxis']

    if jsName=="Highway Construction, Maintenance, and Safety":
         return ['engineering, architecture','construction, unclass','public works, industrial']

    if jsName=="Airports, Airlines, Air Traffic Control and Safety":
         return ['airlines','express delivery','aircraft parts','aircraft manufacturers','aviation services','air transport']

    if jsName=="Railroad Transportation and Safety":
         return ['railroads','railroad services','railroad transport']

    if jsName=="Truck and Automobile Transportation and Safety":
         return ['auto manufacturers','truck/automotive parts','trucking companies','truck & trailer manufacturers','truckingSTOP']

    if jsName=="Maritime Issues":
         return ['sea freight','ship building','sea transport']

    if jsName=="Public Works (Infrastructure Development)":
         return ['public works, industrial','construction & public']

    if jsName=="Research and Development" and jsTopicName.find('ansportation') > -1:
         return []

def map_all_st_to_bus():
    for bus in MapLightBusiness.objects.all():
        bus.subtopics=[]
        bus.save()
    
    
    for st in JonesSubTopic.objects.all():
        if st.name.lower().find('general') > -1:
            continue
        if st.name.lower().find('other') > -1:
            continue
        
        print 'SUBTOPIC NAME ' + st.name
        ret = mapJonesSubToMaplightBusiness(st.name,st.topic.name)
        print ret
        if ret:
            for busName in ret:
                print 'BUSINESS RETURNED: ' + busName
                if busName.find('STOP') == -1:
                    lsBus = MapLightBusiness.objects.filter(name__istartswith=busName)
                else:
                    busName = busName.split('STOP')[0]
                    lsBus = MapLightBusiness.objects.filter(name__iexact=busName)
                
                if len(lsBus) > 0:
                    for mlb in lsBus:
                        newSub = list(mlb.subtopics.all())
                        newSub.append(st)
                        mlb.subtopics = newSub
                        mlb.save()
                    
                    
                    
                print lsBus
                
                
        print "------------------------"   
    
    
if __name__ == '__main__':
    map_all_st_to_bus()
    print "&&&&&&&&&&"
    for bus in MapLightBusiness.objects.all():
        print bus
        print bus.subtopics.all()
        print ""
    
    
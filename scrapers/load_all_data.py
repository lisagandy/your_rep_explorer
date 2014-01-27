from ccu_gen_beta.models import *
from create_states_districts import *
from download_state_district_states import *
from load_jones import *
from load_contributions import *
from download_reps import *
from download_industries import *
from download_rep_stats import *
from download_amendments import *
from download_votes import *
from find_anomalous_votes import *
from paths import *
from classify_with_weka import *

congress111 = Congress.objects.get_or_create(number=111,beginDate=date(2009,1,3),endDate=date(2011,1,3))
congress112 = Congress.objects.get_or_create(number=112,beginDate=date(2011,1,3),endDate=date(2013,1,3))
print 'SAVED CONGRESSIONAL SESSIONS 111 and 112'

#CREATE JONES TOPIC AND SUBTOPICS
loadJones()
print 'SAVED JONES TOPICS AND SUBTOPICS'

#CREATE MAPLIGHT SECTORS, INDUSTRIES, AND BUSINESSES
loadMapLightInterestGroups()
mapMLBusinessToSubtopics()
print 'LOADED MAPLIGHT INTEREST GROUPS'

#CREATE STATES, DISTRICTS
#such as population 
createStates()
print 'LOADED STATE NAMES'
createDistricts()
print 'CREATED DISTRICTS'

#GET REP/SENATOR INFO
loadReps('http://www.govtrack.us/data/us/111/people.xml')
loadReps('http://www.govtrack.us/data/us/112/people.xml')
downloadPics('http://www.govtrack.us/data/photos/')

#DOWNLOAD BILL INFO
#BASIC INFO
loadBasicBillInfo(111)
loadBasicBillInfo(112)
#downloadBillSubjects(111)
#downloadBillSubjects(112)
downloadOrgStanceBill(111)
downloadOrgStanceBill(112)

#DOWNLOAD AMENDMENT INFO
downloadAmendments(111)
downloadAmendments(112)

#DOWNLOAD VOTING INFO
downloadSenateVotes(111)
downloadSenateVotes(112)

#DETERMINE ANOMALOUS VOTES
findAnomReps(vote)

#FIND SUBTOPICS
findJonesSubTopicVotes(111)
findJonesSubTopicVotes(112)

#MAP BUSINESSES AND INDUSTRIES TO JONES
map_all_st_to_bus()
mapAllJonesNAICS()

#GET STATISTICS FOR STATES AND DISTRICTS
getStatePops()
print 'LOADED LATEST STATE POPULATIONS'
getStatePVI(2010)
getDistrictPVI(2010)
print 'LOADED STATE AND DISTRICT PVI'

#GET STATS FOR REPS/SENATORS
getADAStatsSenate2009(CCU_DATA_PATH + 'ada_2009.txt')
getADAStatsSenate2010()
getPartyPercentage(112,senate=False)        
getPartyPercentage(112,senate=True) 
getPartyPercentage(111,senate=False)        
getPartyPercentage(111,senate=True)

#GET COMMITTEES FOR HOUSE AND SENATE
loadCommittees(111)
loadCommittees(112)
mapCommitteesToTopics()

#GET CONTRIBUTION DATA (THIS TAKES FOREVER...)
loadIGContributions(CCU_DATA_PATH + 'campaign contributions/contributions.fec.2002.csv',2002)  
loadIGContributions(CCU_DATA_PATH + 'campaign contributions/contributions.fec.2004.csv',2004)
loadIGContributions(CCU_DATA_PATH + 'campaign contributions/contributions.fec.2006.csv',2006)
loadIGContributions(CCU_DATA_PATH + 'campaign contributions/contributions.fec.2008.csv',2008)
loadIGContributions(CCU_DATA_PATH + 'campaign contributions/contributions.fec.2010.csv',2010)

#DOWNLOAD INDUSTRY INFO (ALSO CREATE MAPPING WITH MAPLIGHT)
getStateIndustries()

#GET ELECTION PREDICTIONS
createElectionDates()
getMostCurrElectionPredSenate()
#for 2010 race
getOldElectionPredsSenate('http://www.cookpolitical.com/node/10438')
getMostCurrElectionPredsHouse()
#first url is for general, second url is for summary for house
getOldElectionPredsHouse('http://www.cookpolitical.com/node/10439','http://www.cookpolitical.com/node/10446')

findExps(111)
findExps(112)
assignPoints(111)
assignPoints(112)
generateVoteDescripts(111)
generateVoteDescripts(112)
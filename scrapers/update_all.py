#this function downloads new voting data...
import os
import sys
from paths import *
sys.path.append('%sccu_beta/generation/' % CCU_PATH)
from download_bills import *
from download_amendments import *
from download_votes import *
from load_elections import *
from find_exps import *
from find_anomalous_votes import *
from classify_with_weka import findJonesSubTopicVotes

def update_bills(sessionNum):
    #Bill.objects.all().update(subtopicsAssigned=True)
    command = "cd %s%d_bills/" % (CCU_DATA_PATH,sessionNum)
    print os.popen(command)
    command = "rsync -az --delete --delete-excluded govtrack.us::govtrackdata/us/%d/bills %s%d_bills/" % (sessionNum,CCU_DATA_PATH,sessionNum)
    loadBasicBillInfo(sessionNum)
    
def update_amendments(sessionNum):
    #Amendment.objects.all().update(subtopicsAssigned=True)
    command = "cd %s%d_amendments/" % (CCU_DATA_PATH,sessionNum)
    print os.popen(command)
    command = "rsync -az --delete --delete-excluded govtrack.us::govtrackdata/us/%d/bills.amdt %s%d_amendments/" % (sessionNum,CCU_DATA_PATH,sessionNum)
    print os.popen(command)
    downloadAmendments(sessionNum)
    
def update_votes(sessionNum):
    Vote.objects.all().update(active=False)
    command = "cd %s%d_votes/" % (CCU_DATA_PATH,sessionNum)
    print os.popen(command)
    command = "rsync -az --delete --delete-excluded govtrack.us::govtrackdata/us/%d/rolls %s%d_votes/" % (sessionNum,CCU_DATA_PATH,sessionNum)
    print os.popen(command)
    downloadSenateVotes(sessionNum)
    findJonesSubTopicVotes()
    
def findExplanations(sessionNum):
    getMostCurrElectionPredsSenate()
    analyzeVoteReps(sessionNum)
    findAllExps(sessionNum)
    
    
if __name__ == '__main__':
    #update_bills(112)    
    #update_bills(112)  
    #update_bills(112)  
    #update_amendments(112)
    #update_votes(112)
    findExplanations(112)
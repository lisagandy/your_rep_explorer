from ccu_gen_beta.models import *

def findAnomReps(vote):
    
    #look at who sponsored the bill
    sponsorParty = None
    try:
        sponsorParty = vote.bill.sponsor.party.lower()
        if vote.hasAmendment:
            sponsorParty = vote.amendment.sponsor.party.lower()
       
    except Exception:
        print 'why no sponsor for vote %s ' % vote
        return
    
    #print sponsorParty
    
    #look at who from the opposite party of the sponsored
    #voted strangely
    if vote.question.lower().find('table') == -1:
        #pass
        oppParty = 'r'
        if sponsorParty.lower().find('r') > -1:
            oppParty = 'd'
    
        anomV = AnomVoters(vote=vote)
        numAye = vote.repVotes.filter(rep__party__icontains=oppParty,voteCast='AYE').count()
        numNay = vote.repVotes.filter(rep__party__icontains=oppParty,voteCast='NAY').count()
    
        if numNay > numAye: #verify as usual that opposite party voted against
            weirdVotersOpp = vote.repVotes.filter(rep__party__icontains=oppParty,voteCast='AYE')
            try:
                print weirdVotersOpp
            except Exception:
                pass
            if oppParty.lower().find('r') > -1: anomV.repVoters = weirdVotersOpp
            else: anomV.demVoters = weirdVotersOpp
        
        
        #look at who from the same party voted strangely
        numAye = vote.repVotes.filter(rep__party__icontains=sponsorParty,voteCast='AYE').count()
        numNay = vote.repVotes.filter(rep__party__icontains=sponsorParty,voteCast='NAY').count()
        if numAye > numNay: #verify as usual that same party voted for
            weirdVotersSame = vote.repVotes.filter(rep__party__icontains=sponsorParty,voteCast='NAY')
            try:
                print weirdVotersSame
            except Exception:
                pass
            if sponsorParty.lower().find('r') > -1: anomV.repVoters = weirdVotersSame
            else: anomV.demVoters = weirdVotersSame
    
        if anomV.repVoters.all().count() > 0 or anomV.demVoters.all().count() > 0:    
            anomV.save()
    else: #for voting on tabling... the opposite applies
        #print vote
        #AnomVoters.objects.filter(vote=vote).delete()
        oppParty = 'r'
        if sponsorParty.lower().find('r') > -1:
            oppParty = 'd'
    
        anomV = AnomVoters(vote=vote)
        numAye = vote.repVotes.filter(rep__party__icontains=oppParty,voteCast='AYE').count()
        numNay = vote.repVotes.filter(rep__party__icontains=oppParty,voteCast='NAY').count()
    
        if numAye > numNay: #verify as usual that opposite party voted against
            weirdVotersOpp = vote.repVotes.filter(rep__party__icontains=oppParty,voteCast='NAY')
            try:
                print weirdVotersOpp
            except Exception:
                pass
            if oppParty.lower().find('r') > -1: anomV.repVoters = weirdVotersOpp
            else: anomV.demVoters = weirdVotersOpp
        
        
        #look at who from the same party voted strangely
        numAye = vote.repVotes.filter(rep__party__icontains=sponsorParty,voteCast='AYE').count()
        numNay = vote.repVotes.filter(rep__party__icontains=sponsorParty,voteCast='NAY').count()
        if numNay > numAye: #verify as usual that same party voted for
            weirdVotersSame = vote.repVotes.filter(rep__party__icontains=sponsorParty,voteCast='AYE')
            try:
                print weirdVotersSame
            except Exception:
                pass
            if sponsorParty.lower().find('r') > -1: anomV.repVoters = weirdVotersSame
            else: anomV.demVoters = weirdVotersSame
    
        if anomV.repVoters.all().count() > 0 or anomV.demVoters.all().count() > 0:    
            anomV.save()
        print anomV
    assert 0  

def analyzeVoteReps(session):

    for i,vote in enumerate(Vote.objects.filter(bill__congress__number=session)):#,bill__number='3217',bill__prefix='s',number=156)):
        if AnomVoters.objects.filter(vote=vote).count() > 0:
            continue
            
        print i
        print vote
        print "-----------------------"
        findAnomReps(vote)

if __name__ == '__main__':
    #AnomVoters.objects.all().delete()
    #analyzeVoteReps(111)
    analyzeVoteReps(112)
    
from ccu_gen_beta.models import *
from ccu_utilities import *
from pyUtilities import *
import string
import numpy
from BeautifulSoup import BeautifulSoup
import urllib
import csv
from django.utils.encoding import smart_str, smart_unicode

for rep in Rep.objects.filter(congress__number=111,senator=True):
	print smart_unicode(rep)
	f = open("/Users/lisa/Desktop/vote_reports_111/%s.csv" % (rep.firstName + '_' + rep.lastName),'w')
	fields = ['vote','subtopic1','subtopic2','subtopic3','topic1','topic2','topic3','anom']
	f.write(",".join(fields)+"\n")
	fDictWriter = csv.DictWriter(f,fields)
	for i,vote in enumerate(Vote.objects.filter(bill__congress__number=111)):
		d={}
		d['vote'] = str(vote)
		d['anom'] = 'no'
		
		subtopics=[]
		if vote.hasAmendment:
			subtopics = vote.amendment.subtopics.all()
		else:
			subtopics = vote.bill.subtopics.all()

		i = 1
		for subtopic in subtopics:
			d['subtopic'+str(i)] = str(subtopic)
			d['topic'+str(i)] = str(subtopic.topic)
			i+=1
			if i==4:
				break

		for i in range(1,4):
			if ('subtopic'+str(i)) not in d.keys():
				d['subtopic'+str(i)] = "NONE"
				d['topic'+str(i)] = "NONE"

		avObj=None
		try:
			avObj = AnomVoters.objects.get(vote=vote)
		except Exception,ex:
			print ex
			print "NO ANOM VOTERS"
	
		if avObj==None:
			continue
			
		demVoters = [dv.rep for dv in avObj.demVoters.all().order_by('rep__lastName')]
		repVoters = [rv.rep for rv in avObj.repVoters.all().order_by('rep__lastName')]
		lsVoter = demVoters
		lsVoter.extend(repVoters)
		#print lsVoter

		if len(lsVoter) == 0:
			fDictWriter.writerow(d)
			continue
		
		if rep in lsVoter:
			print "ANOM VOTER!"
			d['anom'] = 'yes'
		
		fDictWriter.writerow(d)
	f.close()

assert 0					

# for vote in Vote.objects.filter(bill__congress__number=111):
#	 #write out vote number to txt
#	 #write out all info from the vote
#	 #write out bill info
#	 #if has amendment write out amendment info
#	 #lookup up all anomalous voters and print out their info...(name, state)
#	 
#	 #for each anomalous voter: 
#		#look them up in repcontribution report 
#		#look them up in the statepvi report
#		#look them up in the committee report 
#	 


# num_votes = 0
# num_anom_voters=0
# for vote in Vote.objects.filter(bill__congress__number=112):
#	 print vote
#	 avs = AnomVoters.objects.filter(vote=vote)
#	 if avs.count() > 0:
#		num_votes+=1
#		num_anom_voters = num_anom_voters + avs[0].demVoters.count() + avs[0].repVoters.count()
#		
# print num_votes
# print num_anom_voters
# assert 0	 



print RepOrgStanceMoneyVote.objects.filter(repReport__vote__number=35)
assert 0

#print RepContributionReport.objects.filter(vote=Vote.objects.get(number=875,bill__congress__number=111))
#or vr in VoteReport.objects.filter(Q(vote__bill__congress__number=111)|Q(vote__amendment__bill__congress__number=111),hasStance=True):
   #print vr.vote

assert 0
VoteReport.objects.filter(vote__senateVote=True).update(hasInd=False)
for vote in Vote.objects.filter(senateVote=True):
	if NAICSIndustryReport.objects.filter(vote=vote).count() > 0:
		vr = VoteReport.objects.filter(vote=vote)[0]
		vr.hasInd=True
		vr.save()
		print vr

assert 0


for i,rco in enumerate(RepOrgStanceMoneyVote.objects.all()):
	print i
	vote = rco.repReport.vote
	voteReport,isThere = VoteReport.objects.get_or_create(vote=vote)
	voteReport.hasStance=True
	voteReport.save()


assert 0
lsVotes = []
for vote in Vote.objects.filter(senateVote=False,bill__congress__number=112):
	if vote.bill and not vote.amendment and vote.bill.orgStances.all().count() > 0:
		if RepContributionReport.objects.filter(vote=vote).count() > 0:
			lsVotes.append((vote.number,vote.bill.number))

print lsVotes 
assert 0


#print Vote.objects.filter(Q(bill__congress__number=111)|Q(amendment__bill__congress__number=111)).count()
print(Bill.objects.filter(congress__number=111).count())
assert 0
#VoteReport.objects.all().delete()
for i,vote in enumerate(Vote.objects.all()):
	print(i)
	#get top 5 anonamous voters...
	trs = TempRepPoints.objects.filter(vote=vote).exclude(points=0).order_by('-points')
	if len(trs) > 0:
		trs = trs[0:5]
	
	reps = [tr.rep for tr in trs]
	if len(reps)==0:
		continue
	
	vr,isThere	= VoteReport.objects.get_or_create(vote=vote)
	if PredElectionReport.objects.filter(vote=vote,predElection__rep__in=reps)[:1].count() > 0:
		vr.hasElec = True
		vr.save()
	if StatePVIReport.objects.filter(vote=vote,rep__in=reps)[:1].count() > 0:
		vr.hasDiff = True
		vr.save()
	if ChairCommitteeReport.objects.filter(vote=vote,rep__in=reps)[:1].count() > 0:
		vr.hasComm=True
		vr.save()
	if NAICSIndustryReport.objects.filter(vote=vote,rep__in=reps)[:1].count() > 0:
		vr.hasInd=True
		vr.save()
	repContr_all = RepContributionReport.objects.filter(vote=vote,rep__in=reps)
	if repContr_all.count() > 0:   
		vr.hasContr = True
		vr.save()

	if not vote.hasAmendment:
		reps = list(set(repContr_all.values_list('rep',flat=True)))	  
		sectors = list(set(repContr_all.values_list('bus__industry__sector',flat=True)))	
		for rep in reps:
			if vr.hasStance:
				break
			amtFor = 0
			amtAgainst = 0
			for sector in sectors:
				repContr_buses = repContr_all.filter(bus__industry__sector=sector,rep=rep)
				for rc in repContr_buses:
					amtFor += rc.amtMoneyFor
					amtAgainst += rc.amtMoneyAgainst
				
				if amtFor >=20000 or amtAgainst >=20000:
					vr.hasStance=True
					vr.save()
					break
assert 0
def biPartisanVoterTF(rep,vote):
	if RepWithPartyReport.objects.filter(vote=vote,repWithParty__rep=rep).count() > 0:
		  return
	
	try:
	   rwObj = RepWithParty.objects.get(rep=rep)
	except Exception:
	   return
	
	congress = rep.congress
	if congress.number not in partyPercentD:
		addPartyPercentD(congress.number)
  
	isOut,typeOut = isOutlier(rwObj.withPartyScore,partyPercentD[congress.number])
	   
	if isOut and typeOut.find('LOW') > -1:
		 return True
	else:
		return False

print(Vote.objects.all().count())


# VoteReport.objects.all().update(hasContr=False)
# i=0
# print VoteReport.objects.all().count()
# for vr in VoteReport.objects.all():
#	  i+=1
#	  print i
#	  if RepContributionReport.objects.filter(vote=vr.vote)[:1].count() > 0:
#		  vr.hasContr=True
#		  vr.save()
# 
# assert 0

PercentWithPartyStats.objects.all().delete()
for dateCut in [date(2010,12,31), date(2011,12,31)]:
	for subtopic in JonesSubTopic.objects.all():
		pcs = PercentWithParty.objects.filter(lastVoteDate=dateCut,subtopic=subtopic)
		if pcs.count() == 0:
			continue
			
		lsPC = [pc.percentage() for pc in pcs]
		lsPC.sort()
		list1 = lsPC[0:int(len(lsPC)/2)]
		list2 = lsPC[int(len(lsPC)/2+0.5):]
		
		if PercentWithPartyStats.objects.filter(lastVoteDate=dateCut,subtopic=subtopic).count()==0:
			statObj = PercentWithPartyStats(lastVoteDate=dateCut,subtopic=subtopic,median=0,mean=0,std=0)
			statObj.high_range = numpy.median(list2)
			statObj.low_range = numpy.median(list1)
			statObj.mean = numpy.mean(lsPC)
			statObj.median = numpy.median(lsPC)
			statObj.std = numpy.std(lsPC)
			statObj.save()
			print(statObj)

assert 0

#PercentWithParty.objects.all().delete()
for dateCut in [date(2010,12,31), date(2011,12,31)]:
	for subtopic in JonesSubTopic.objects.all():
		for rep in Rep.objects.filter(senator=True):
			if Vote.objects.filter(Q(bill__subtopics=subtopic)|Q(amendment__subtopics=subtopic),dateVote__lte=dateCut,repVotes__rep__repID=rep.repID).count()==0:
				continue
			
			if PercentWithParty.objects.filter(lastVoteDate=dateCut,subtopic=subtopic,rep__repID=rep.repID).count() == 0:
				pc = PercentWithParty(subtopic=subtopic,lastVoteDate=dateCut,rep=rep)
				votes = Vote.objects.filter(Q(bill__subtopics=subtopic)|Q(amendment__subtopics=subtopic),dateVote__lte=dateCut,repVotes__rep__repID=rep.repID)
				numVotes = votes.count()
				numAgainstParty = 0 
				for vote in votes:
					if rep.party=='D':
						if AnomVoters.objects.filter(vote=vote,demVoters__rep__repID=rep.repID).count() > 0:
							numAgainstParty+=1
					elif rep.party=='R':
						if AnomVoters.objects.filter(vote=vote,repVoters__rep__repID=rep.repID).count() > 0:
							numAgainstParty+=1
					#print numAgainstParty		  
				pc.numWithParty=numVotes - numAgainstParty
				pc.numVotes=numVotes
				pc.save()
				if pc.percentage() > 0:
					try:
						print(pc)
					except Exception:
						pass
				if pc.percentage() > 100:
					print(pc)
					assert 0
assert 0

print(Vote.objects.filter(Q(bill__congress__number=111)|Q(amendment__bill__congress__number=111)).count())
assert 0


# from django.contrib import admin
# admin.autodiscover()
# print admin.site.urls
# assert 0
# 

from .ccu_gen_beta.models import *
from ccu_utilities import *

print(Organization.objects.filter(orgName__icontains='j.p. Morgan'))
9360077
print(RepContribution.objects.filter(rep__lastName='Dodd',contribName__icontains='morgan'))

assert 0
rcs = RepContribution.objects.filter(rep__lastName='Johanns',mlBusiness__industry__name__icontains='Food process')
total =	 rcs.aggregate(Sum('amountContr'))['amountContr__sum']
print(total)

allRCS = RepContribution.objects.filter(rep__lastName='Johanns')
total2 =  allRCS.aggregate(Sum('amountContr'))['amountContr__sum']
print(total2)

print((total/float(total2)) * 100)
assert 0

# for rc in RepContributionTotalAmounts.objects.all():
#	  print long(rc.totalAmt)
# 
# assert 0
print(RepContributionReport.objects.all().count())

i = 0
for rc in RepContributionReport.objects.all():
	print('count')
	print(i)
	
	try:
		totalRC = RepContributionTotalAmounts.objects.get_or_create(beginDate=rc.startDate,endDate=rc.endDate,rep=rc.rep)
	except Exception:
		pass
	if totalRC[0].totalAmt > 0:
		continue
	else:
		totalRC=totalRC[0]
	
	rcs = RepContribution.objects.filter(rep=rc.rep,dateContr__lte=rc.endDate,dateContr__gte=rc.startDate)
	try:
		print(rc.rep)
	except Exception:
		pass
		
	totalAmt = rcs.aggregate(Sum('amountContr'))['amountContr__sum']
	totalRC.totalAmt = totalAmt
	totalRC.rcs=rcs
	totalRC
	print('totalAmt')
	print(totalRC.totalAmt)
	try:
		print(totalRC.rep)
	except Exception:
		pass

assert 0


bill =	Bill.objects.get(congress__number=111,number=3217,prefix='s')
# osPos = bill.orgStances.filter(against=True)
# osPosName = [orgstance.org.orgName for orgstance in osPos]
osNeg = bill.orgStances.filter(against=False)
osNegName = [orgstance.org.orgName for orgstance in osNeg]

for vote in Vote.objects.filter(bill__prefix='s',bill__number=3217):
		
		print(vote)
		print("-------------------------")
		avs = AnomVoters.objects.filter(vote=vote)
		for av in avs:
			try:
				for voter in av.demVoters.all():
					
					rcs = RepContribution.objects.filter(rep=voter,dateContr__lte=vote.dateVote,contribName__in=osNegName)
					mlBuses = [rc.mlBusiness for rc in rcs]
					amt = rcs.aggregate(Sum('amountContr'))['amountContr__sum']
					if amt and amt > 20000:
						print(voter)
						print("***************")
						print(amt)
						print(mlBuses)
				
				for voter in av.repVoters.all():
				   
					rcs = RepContribution.objects.filter(rep=voter,dateContr__lte=vote.dateVote,contribName__in=osNegName)
					amt = rcs.aggregate(Sum('amountContr'))['amountContr__sum']
					mlBuses = [rc.mlBusiness for rc in rcs]
					if amt and amt > 20000:
						print(voter)
						print("***************")
						print(amt)
						print(mlBuses)
			except Exception:
				print("problem with printing")
				
		print("")
		print("")
		print("")	 
	
	#print RepContribution.objects.filter(contribName__icontains=orgstance.org.orgName)
	#print RepContribution.objects.filter(contribEmployerloyer__icontains=orgstance.org.orgName)
	#print ""
assert 0	

# for vote in Vote.objects.all():
#	  voteReport = VoteReport.objects.get_or_create(vote=vote)[0]
#	  if NAICSIndustryReport.objects.filter(vote=vote).count() > 0:
#		  voteReport.hasInd=True
#		  voteReport
#		  print vote
# assert 0


	
# for vote in Vote.objects.all():
#			  hasPVI=False
#			  if StatePVIReport.objects.filter(vote=vote).count() > 0:
#				  hasPVI=True
#			  #print 'HERE2'
#			  
#			  hasContr=False
#			  if RepContributionReport.objects.filter(vote=vote).count() > 0:
#				  hasContr=True
#			  #print 'HERE3'
#			  
#			  hasInd=False
#			  if NAICSIndustryReport.objects.filter(vote=vote).count() > 0:
#				  hasInd=True
#			  #print 'HERE4'
#			  
#			  hasOther=False
#			  if PredElectionReport.objects.filter(vote=vote).count() > 0:
#				  hasOther=True
#			  #print 'HERE5'
#			  
#			  hasComm=False
#			  if ChairCommitteeReport.objects.filter(vote=vote).count() > 0:
#				  hasComm=True
#		 
#			  voteReport = VoteReport.objects.get_or_create(vote=vote,hasElec=hasOther,hasContr=hasContr,hasComm=hasComm,hasDiff=hasPVI)[0]
#			  voteReport
#			  print voteReport.vote
#			  print voteReport.hasContr
# 
# assert 0

# allrcs = RepContributionReport.objects.all()
# print allrcs.count()
# i = 0
# for rc in allrcs:
#	  print i
#	  i+=1
#	  if rc.totalAmt > 0: continue
#	  rc.totalAmt = rc.totalAmtCalc()
#	  rc
#	  print rc.totalAmt
#	  
# assert 0

#!/usr/bin/env python

import re
import fileinput

def this_line_is_useless(line):
	useless_es = [
		'BEGIN TRANSACTION',
		'COMMIT',
		'sqlite_sequence',
		'CREATE UNIQUE INDEX',	 
		'PRAGMA foreign_keys=OFF'		  
		]
	for useless in useless_es:
		if re.search(useless, line):
			return True

searching_for_end = False
outfile = open('/Users/lisagandy/infolab_projects/dump_cleaned2.sql','w')
for line in fileinput.input('/Users/lisagandy/infolab_projects/dump.sql'):
	if this_line_is_useless(line): continue
   
	line = line.replace('"', '`')
	line = line.replace("\\",'')
	line.replace('autoincrement','auto_increment')
	outfile.write(line)
	#print 'WROTE LINE'
	# try:
	#		  print line
	#	  except Exception:
	#		  pass
assert 0
# CREATE TABLE "ccu_gen_beta_naics_industry_subtopics" (
#	  "id" integer NOT NULL PRIMARY KEY,
#	  "naics_industry_id" integer NOT NULL REFERENCES "ccu_gen_beta_naics_industry" ("id"),
#	  "jonessubtopic_id" integer NOT NULL REFERENCES "ccu_gen_beta_jonessubtopic" ("id"),
#	  UNIQUE ("naics_industry_id", "jonessubtopic_id")
# );
# 
# CREATE TABLE "ccu_gen_beta_bill_subtopics" ("id" integer NOT NULL PRIMARY KEY,"bill_id" integer NOT NULL REFERENCES "ccu_gen_beta_bill" ("id"),"jonessubtopic_id" integer NOT NULL REFERENCES "ccu_gen_beta_jonessubtopic" ("id"),UNIQUE ("bill_id", "jonessubtopic_id"));
# 
from .ccu_gen_beta.models import *

print(NAICS_Locale.objects.filter(state__name='MONTANA',naicsIndustry__name='Hospitals')[0].numEmployees/float(StatePop.objects.filter(state__name='MONTANA')[0].pop))
assert 0

numReports=0
totalEmployees=0
for congress in [111,112]:
	for state in State.objects.all():
		localState = NAICS_Locale.objects.filter(state=state,naicsIndustry__name='Hospitals')
		if len(localState) > 0:
			for report in localState:
				totalEmployees+=(report.numEmployees/float(StatePop.objects.filter(state=state)[0].pop))
				numReports+=1

print(totalEmployees/float(numReports))
assert 0

dMoney = {}
busName = []
for congress in [111,112]:
	for rep in Rep.objects.filter(senator=True,congress__number=congress):
		bus_names=['life insurance','commercial banks','insurance brokers','security brokers','investment banking']
		repName = rep.officialName()
		print(repName)
		if repName not in dMoney:
			dMoney[repName] = {}
		
		for bus in bus_names:
			rcs2 = RepContributionReport.objects.filter(rep=rep,mlBusiness__name__icontains=bus) 
			for rc in rcs2:
				if rc.mlBusiness.name in dMoney[repName]:
					dMoney[repName][rc.mlBusiness.name] += rc.totalAmt()
				else:
					dMoney[repName][rc.mlBusiness.name] = rc.totalAmt()
				if rc.mlBusiness.name not in busName:
					busName.append(rc.mlBusiness.name)
					
#Money = {u'Sen. Sherrod Brown [D,OH]': {}, u'Sen. Daniel Akaka [D,HI]': {}, u'Sen. Jim Webb [D,VA]': {u'Investment banking': 30050.0}, u'Sen. Hillary Clinton [D,NY]': {}, u'Sen. Kelly Ayotte [R,NH]': {}, u'Sen. Kent Conrad [D,ND]': {}, u'Sen. Debbie Ann Stabenow [D,MI]': {}, u'Sen. Bob Corker [R,TN]': {u'Commercial banks & bank holding companies': 182333.0, u'Security brokers & investment companies': 391323.0}, u'Sen. Michael Bennet [D,CO]': {u'Life insurance': 25200.0, u'Investment banking': 13500.0, u'Commercial banks & bank holding companies': 12300.0, u'Security brokers & investment companies': 59795.0}, u'Sen. Sheldon Whitehouse [D,RI]': {u'Investment banking': 44750.0}, u'Sen. Arlen Specter [D,PA]': {u'Life insurance': 97100.0, u'Investment banking': 217886.0, u'Commercial banks & bank holding companies': 226000.0, u'Security brokers & investment companies': 513200.0}, u'Sen. Mitch McConnell [R,KY]': {u'Investment banking': 77050.0, u'Commercial banks & bank holding companies': 363425.0, u'Security brokers & investment companies': 636760.0}, u'Sen. Joe Manchin [D,WV]': {u'Commercial banks & bank holding companies': 40300.0, u'Security brokers & investment companies': 11950.0}, u'Sen. Mark Udall [D,CO]': {}, u'Sen. Barbara Mikulski [D,MD]': {}, u'Sen. Chuck Grassley [R,IA]': {u'Life insurance': 198400.0}, u'Sen. Ben Nelson [D,NE]': {u'Life insurance': 130150.0}, u'Sen. Joseph Lieberman [I,CT]': {u'Commercial banks & bank holding companies': 187432.0}, u'Sen. Daniel Coats [R,IN]': {}, u'Sen. Ken Salazar [D,CO]': {}, u'Sen. Jeanne Shaheen [D,NH]': {}, u'Sen. Pat Toomey [R,PA]': {}, u'Sen. Paul Kirk [D,MA]': {}, u'Sen. Michael Enzi [R,WY]': {}, u'Sen. Lamar Alexander [R,TN]': {u'Commercial banks & bank holding companies': 213100.0}, u'Sen. Marco Rubio [R,FL]': {}, u'Sen. John Hoeven [R,ND]': {}, u'Sen. Michael Crapo [R,ID]': {}, u'Sen. Olympia Snowe [R,ME]': {u'Life insurance': 109484.0}, u'Sen. Tom Harkin [D,IA]': {u'Investment banking': 74135.0}, u'Sen. David Vitter [R,LA]': {u'Investment banking': 73803.0}, u'Sen. Mary Landrieu [D,LA]': {u'Life insurance': 115978.0}, u'Sen. Richard Burr [R,NC]': {u'Investment banking': 81911.0, u'Commercial banks & bank holding companies': 329749.0}, u'Sen. Mark Pryor [D,AR]': {}, u'Sen. Carl Levin [D,MI]': {}, u'Sen. Byron Dorgan [D,ND]': {}, u'Sen. Mel Martinez [R,FL]': {u'Investment banking': 79003.0, u'Commercial banks & bank holding companies': 225450.0, u'Security brokers & investment companies': 304157.0}, u'Sen. Evan Bayh [D,IN]': {u'Life insurance': 82699.0, u'Investment banking': 261400.0, u'Commercial banks & bank holding companies': 203994.0, u'Security brokers & investment companies': 513664.0}, u'Sen. Roland Burris [D,IL]': {}, u'Sen. Saxby Chambliss [R,GA]': {u'Life insurance': 105205.0, u'Commercial banks & bank holding companies': 315148.0}, u'Sen. Kirsten Gillibrand [D,NY]': {}, u'Sen. Jim Bunning [R,KY]': {u'Life insurance': 86333.0}, u'Sen. Lindsey Graham [R,SC]': {}, u'Sen. John Boozman [R,AR]': {}, u'Sen. Blanche Lincoln [D,AR]': {u'Life insurance': 111550.0, u'Investment banking': 109450.0, u'Commercial banks & bank holding companies': 238157.0, u'Security brokers & investment companies': 320666.0}, u'Sen. Richard Shelby [R,AL]': {u'Life insurance': 119899.0, u'Investment banking': 77000.0, u'Commercial banks & bank holding companies': 402697.0, u'Security brokers & investment companies': 399183.0}, u'Sen. Robert Byrd [D,WV]': {}, u'Sen. Bill Nelson [D,FL]': {}, u'Sen. Al Franken [D,MN]': {u'Investment banking': 42950.0}, u'Sen. Mike Johanns [R,NE]': {u'Life insurance': 37550.0, u'Investment banking': 25600.0, u'Commercial banks & bank holding companies': 91550.0}, u'Sen. Barbara Boxer [D,CA]': {}, u'Sen. Richard Lugar [R,IN]': {}, u'Sen. Claire McCaskill [D,MO]': {}, u'Sen. Robert Bennett [R,UT]': {u'Commercial banks & bank holding companies': 185624.0}, u'Sen. John Kerry [D,MA]': {u'Life insurance': 185851.0, u'Investment banking': 929442.0, u'Commercial banks & bank holding companies': 1092430.0, u'Security brokers & investment companies': 2662482.0}, u'Sen. Mark Kirk [R,IL]': {}, u'Sen. Carte Goodwin [D,WV]': {}, u'Sen. John McCain [R,AZ]': {u'Life insurance': 290103.0, u'Investment banking': 1236855.0, u'Commercial banks & bank holding companies': 1840238.0, u'Security brokers & investment companies': 4713533.0}, u'Sen. Max Baucus [D,MT]': {u'Life insurance': 309400.0, u'Investment banking': 183350.0, u'Commercial banks & bank holding companies': 317407.0, u'Security brokers & investment companies': 480334.0}, u'Sen. Richard Blumenthal [D,CT]': {}, u'Sen. Jack Reed [D,RI]': {u'Investment banking': 95519.0, u'Commercial banks & bank holding companies': 243899.0}, u'Sen. Maria Cantwell [D,WA]': {u'Security brokers & investment companies': 318768.0}, u'Sen. John Barrasso [R,WY]': {u'Commercial banks & bank holding companies': 39450.0}, u'Sen. Kirsten Gillibrand': {}, u'Sen. Daniel Inouye [D,HI]': {}, u'Sen. Johnny Isakson [R,GA]': {u'Commercial banks & bank holding companies': 188369.0}, u'Sen. Benjamin Cardin [D,MD]': {}, u'Sen. Jon Tester [D,MT]': {}, u'Sen. Ron Wyden [D,OR]': {}, u'Sen. Charles Schumer [D,NY]': {u'Investment banking': 526190.0, u'Commercial banks & bank holding companies': 577000.0}, u'Sen. Mark Begich [D,AK]': {u'Investment banking': 10900.0, u'Security brokers & investment companies': 63362.0}, u'Sen. Joseph Biden [D,DE]': {}, u'Sen. Tom Udall [D,NM]': {}, u'Sen. Jeff Sessions [R,AL]': {u'Life insurance': 81600.0}, u'Sen. Chris Coons [D,DE]': {}, u'Sen. Roger Wicker [R,MS]': {}, u'Sen. John Ensign [R,NV]': {}, u'Sen. Ron Johnson [R,WI]': {}, u'Sen. Orrin Hatch [R,UT]': {u'Investment banking': 85200.0}, u'Sen. Patrick Leahy [D,VT]': {}, u'Sen. Richard Durbin [D,IL]': {}, u'Sen. Jim Inhofe [R,OK]': {}, u'Sen. Tim Johnson [D,SD]': {u'Life insurance': 149500.0, u'Investment banking': 76980.0, u'Commercial banks & bank holding companies': 275824.0, u'Security brokers & investment companies': 307305.0}, u'Sen. Herb Kohl [D,WI]': {}, u'Sen. Jon Kyl [R,AZ]': {u'Commercial banks & bank holding companies': 174800.0, u'Security brokers & investment companies': 290300.0}, u'Sen. Jay Rockefeller [D,WV]': {}, u'Sen. Thad Cochran [R,MS]': {}, u'Sen. Jeff Bingaman [D,NM]': {}, u'Sen. Thomas Carper [D,DE]': {u'Life insurance': 106640.0, u'Commercial banks & bank holding companies': 273852.0}, u'Sen. Amy Klobuchar [D,MN]': {}, u'Sen. Edward Kaufman [D,DE]': {}, u'Sen. John Thune [R,SD]': {}, u'Sen. Lisa Murkowski [R,AK]': {}, u'Sen. George LeMieux [R,FL]': {}, u'Sen. Bernie Sanders [I,VT]': {}, u'Sen. Frank Lautenberg [D,NJ]': {u'Investment banking': 140500.0, u'Security brokers & investment companies': 355750.0}, u'Sen. Jerry Moran [R,KS]': {}, u'Sen. Ted Kennedy [D,MA]': {}, u'Sen. Jeff Merkley [D,OR]': {u'Security brokers & investment companies': 91617.0}, u'Sen. Kay Hagan [D,NC]': {u'Commercial banks & bank holding companies': 47683.0, u'Security brokers & investment companies': 74544.0}, u'Sen. Pat Roberts [R,KS]': {}, u'Sen. Robert Casey [D,PA]': {u'Commercial banks & bank holding companies': 108675.0, u'Security brokers & investment companies': 214975.0}, u'Sen. Thomas Coburn [R,OK]': {}, u'Sen. Mike Lee [R,UT]': {}, u'Sen. James Risch [R,ID]': {}, u'Sen. Mark Warner [D,VA]': {u'Life insurance': 60400.0, u'Investment banking': 86310.0, u'Commercial banks & bank holding companies': 103983.0, u'Security brokers & investment companies': 314400.0}, u'Sen. Scott Brown [R,MA]': {u'Life insurance': 13750.0, u'Investment banking': 41100.0, u'Commercial banks & bank holding companies': 33250.0, u'Security brokers & investment companies': 262342.0}, u'Sen. Roy Blunt [R,MO]': {}, u'Sen. Kay Hutchison [R,TX]': {}, u'Sen. Jim DeMint [R,SC]': {u'Investment banking': 78063.0, u'Security brokers & investment companies': 297883.0}, u'Sen. Kit Bond [R,MO]': {}, u'Sen. Rob Portman [R,OH]': {}, u'Sen. Judd Gregg [R,NH]': {}, u'Sen. Susan Collins [R,ME]': {u'Life insurance': 82250.0}, u'Sen. Bob Men\xe9ndez [D,NJ]': {u'Life insurance': 139200.0, u'Investment banking': 219500.0, u'Commercial banks & bank holding companies': 208150.0, u'Security brokers & investment companies': 444038.0}, u'Sen. Christopher Dodd [D,CT]': {u'Life insurance': 324056.0, u'Investment banking': 808700.0, u'Commercial banks & bank holding companies': 952894.0, u'Security brokers & investment companies': 2291889.0}, u'Sen. Patty Murray [D,WA]': {}, u'Sen. George Voinovich [R,OH]': {u'Commercial banks & bank holding companies': 252255.0}, u'Sen. Rand Paul [R,KY]': {}, u'Sen. Sam Brownback [R,KS]': {}, u'Sen. Dianne Feinstein [D,CA]': {}, u'Sen. Harry Reid [D,NV]': {u'Life insurance': 118300.0, u'Investment banking': 141300.0, u'Commercial banks & bank holding companies': 230996.0, u'Security brokers & investment companies': 471470.0}, u'Sen. Russell Feingold [D,WI]': {}, u'Sen. John Cornyn [R,TX]': {u'Investment banking': 96100.0, u'Commercial banks & bank holding companies': 442592.0, u'Security brokers & investment companies': 450875.0}}
print(dMoney)			 
print(len(list(dMoney.keys())))
avgNum = len(list(dMoney.keys()))
dAvg = {}
for bus in busName:
	dAvg[bus] = 0
	numBus = 0
	for repName in list(dMoney.keys()):
		try:
			dAvg[bus] += dMoney[repName][bus]
		except Exception as ex:
			print(ex)
			pass
	dAvg[bus] = dAvg[bus] / len(list(dMoney.keys()))
	
print(dAvg)
assert 0


# lastName='mccain'
# print Rep.objects.filter(lastName__iexact=lastName)
# assert 0
#print Rep.objects.filter(lastName='Nelson')

rep = Rep.objects.filter(lastName='Baucus',firstName='Max')
# 
# # num of anomalous votes
votes = AnomVoters.objects.filter(demVoters__rep__in=rep)
print(votes.count())
assert 0
# print votes.count()
votes = AnomVoters.objects.all()

for rep in Rep.objects.filter(party='D',senator=True,lastName='Baucus'):
	try:
		print(rep)
	except Exception as ex:
		continue
		
	rep = [rep]
	#num anomalous votes where a campaign contribution exists
	numRC = 0
	for av in votes:
		if RepContributionReport.objects.filter(vote=av.vote,rep__in=rep).count() > 0:
			numRC+=1
	print(numRC)

	numIR = 0
	for av in votes:
		if NAICSIndustryReport.objects.filter(vote=av.vote,rep__in=rep).count() > 0:
			numIR+=1
	print(numIR)

	numPE = 0
	for av in votes:
		 if PredElectionReport.objects.filter(vote=av.vote,predElection__rep__in=rep).count() > 0:
			  numPE+=1
	print(numPE)

	numDL = 0
	for av in votes:
		if StatePVIReport.objects.filter(vote=av.vote,rep__in=rep).count() > 0:
			numDL+=1
	print(numDL)

	numCC = 0
	for av in votes:
		if ChairCommitteeReport.objects.filter(vote=av.vote,rep__in=rep).count() > 0:
			numCC+=1
	print(numCC)

# for committee in Committee.objects.all():
#	  print committee
#	  print committee.topics.all()
	
def load_vote_refined(request,session,bill_prefix,bill_number,vote_number):
        
        global ref_url


        vote = Vote.objects.filter(bill__congress__number=session,bill__prefix=bill_prefix,bill__number=bill_number,number=vote_number)[0]
        allVoters = None
        try:
            allVoters = [av for av in AnomVoters.objects.get(vote=vote).demVoters.all().order_by('rep__lastName')]
        except Exception as ex:
            print(ex)


        try:
            allVoters.extend([av for av in AnomVoters.objects.get(vote=vote).repVoters.all().order_by('rep__lastName')])
        except Exception:
            pass

        if allVoters:
            try:
                if vote.amendment:
                    subtopic = vote.amendment.subtopics.all()[0]
                else:
                    subtopic = vote.bill.subtopics.all()[0]
            except Exception:
                pass

            allVoters2 = []
            for av in allVoters:
                rep = av.rep
                if vote.dateVote<=date(2010,12,31):
                    searchDate=date(2010,12,31)
                else:
                    searchDate = vote.dateVote

                try:
                    print(PercentWithParty.objects.filter(subtopic=subtopic,rep=rep,lastVoteDate__lte=searchDate).order_by('-lastVoteDate'))
                    pc = PercentWithParty.objects.filter(subtopic=subtopic,rep=rep,lastVoteDate__lte=searchDate).order_by('-lastVoteDate')[0]
                    
                except Exception:
                    continue

                #print pc
                pcStat = PercentWithPartyStats.objects.get(subtopic=subtopic,lastVoteDate=pc.lastVoteDate)
                print(pcStat)
                isOut,typeOut = isOutlierStats(pc .percentage(),pcStat)
                print(isOut)
                print(typeOut)
                print("")
                if (isOut==True and typeOut.find('HIGH') != -1 or not isOut) and pc.percentage() >= (pcStat.median + pcStat.std):
                    allVoters2.append(rep)
        else:
            allVoters2=None

        #print "ALL VOTERS 2"
        #print allVoters2
  
        biPartisan = []
        predElection=[]
        relComm = []
        naicsInd = []
        repData = []
        pviReportDem = []
        pviReportRep = []
        #print allVoters
        if allVoters2:
            for voter in allVoters2:
                print(voter)

                percent = PercentWithParty.objects.filter(subtopic=subtopic,rep=voter,lastVoteDate__lte=searchDate).order_by('-lastVoteDate')[0].percentage()
                pcStats = PercentWithPartyStats.objects.get(subtopic=subtopic,lastVoteDate=pc.lastVoteDate)
                biPartisan.append([voter,percent,pcStats])
                try:
                    predElection.append(PredElectionReport.objects.get(vote=vote,predElection__rep=voter))
                except Exception as ex:
                    pass
                    ##print ex
                    #predElection.append(None)

                try:
                    if voter.party=='D':
                        pviReportDem.append(StatePVIReport.objects.get(vote=vote,rep=voter))
                    elif voter.party=='R':
                        pviReportRep.append(StatePVIReport.objects.get(vote=vote,rep=voter))
                except Exception as ex:
                    pass

                try:
                    relComm.append(ChairCommitteeReport.objects.get(vote=vote,rep=voter))
                except Exception as ex:
                    pass
                    ##print ex
                    #relComm.append(None)

                naicsObjs = NAICSIndustryReport.objects.filter(vote=vote,rep=voter)
                if naicsObjs.count() > 0:
                    naicsInd.extend(naicsObjs)

                # rcObjs = RepContributionReport.objects.filter(vote=vote,rep=voter)
                #                 if rcObjs.count() > 0:
                #                     repData.extend(rcObjs)


        lsRep = []
        lsSector = []
        lsNumBus = []
        lsTotal = []
        lsPercent = []
        lsAverage=[]
        rcs = RepContributionReport.objects.filter(vote=vote,rep__in=allVoters2)
        reps = rcs.values_list('rep',flat=True)
        reps = list(set(reps))
        for rep in reps:
           rcs_rep = rcs.filter(rep=rep)
           sectors = list(set(rcs_rep.values_list('bus__industry__sector',flat=True)))
           for sector in sectors:
               lsRep.append(Rep.objects.get(pk=rep))
               lsSector.append(MapLightSector.objects.get(pk=sector))
               rc_buses = rcs_rep.filter(bus__industry__sector=sector)
               buses = list(set(rc_buses.values_list('bus',flat=True)))
               lsNumBus.append(len(buses))
               lsTotal.append(rc_buses.aggregate(Sum('totalAmt'))['totalAmt__sum'])
               totalAll = RepContributionTotalAmounts.objects.filter(endDate=vote.dateVote,rep=rep)[0].totalAmt
               lsPercent.append((lsTotal[-1]/float(totalAll))*100)
               # rc_av = RepContributionAverage.objects.filter(bus__in=buses,endDate=vote.dateVote)
               #                num=0
               #                denom=0
               #                for rc in rc_av:
               #                    num += (rc.numReps*rc.totalAmt)
               #                    denom += rc.numReps
               #                lsAverage.append(convertMoney(num/float(denom)))

        lsTotal = [convertMoney(total) for total in lsTotal]


        #STOPPED HERE...
        repContr = list(zip(lsPercent,lsRep,lsSector,lsTotal,lsNumBus,lsPercent))
        repContr.sort()
        repContr.reverse()
        lsPercent,lsRep,lsSector,lsTotal,lsNumBus,lsPercent = list(zip(*repContr))
        repContr = list(zip(lsRep,lsSector,lsTotal,lsNumBus,lsPercent))        

        lsRep0=[]
        lsCompanies0=[]
        lsAmtCompInt=[]
        lsAmtComp=[]
        lsCompSector=[]
        lsCompanyStance=[]
        lsCompanySame=[]
        #look at orgstances
        for rep in reps:
            rcs_rep = rcs.filter(rep=rep)
            sectors = list(set(rcs_rep.values_list('bus__industry__sector',flat=True)))
            for sector in sectors:
                rc_buses = rcs_rep.filter(bus__industry__sector=sector)
                lsCompanyStanceH = []
                lsCompanySameH = []
                amtComp = 0
                lsCompanies=[]

                for rc in rc_buses:
                    if rc.amtMoneyFor and rc.amtMoneyFor > 0 and rc.amtMoneyFor > rc.amtMoneyAgainst:
                        lsCompanies.extend(list(rc.orgstancesFor.all()))
                        lsCompanyStanceH.append(True)
                        lsCompanySameH.append(rc.obeyedCompany)
                        amtComp+=rc.amtMoneyFor                
                    elif rc.amtMoneyAgainst and rc.amtMoneyAgainst > 0 and rc.amtMoneyAgainst > rc.amtMoneyFor:
                        lsCompanies.extend(list(rc.orgstancesAgainst.all()))
                        lsCompanyStance.append(False)
                        lsCompanySame.append(rc.obeyedCompany)
                        amtComp+=rc.amtMoneyAgainst

                if amtComp > 20000:
                    lsRep0.append(Rep.objects.get(pk=rep))
                    lsCompanies0.append(lsCompanies)
                    lsAmtCompInt.append(amtComp)
                    lsAmtComp.append(convertMoney(amtComp))
                    lsCompSector.append(MapLightSector.objects.get(pk=sector))
                    numTrue = sum([1 for cs in lsCompanyStance if cs==True])
                    numFalse = len(lsCompanyStance) - numTrue
                    if numTrue > numFalse:
                       lsCompanyStance.append(True)
                    else:
                       lsCompanyStance.append(False)
                    numFor = sum([1 for cs in lsCompanySame if True])
                    numAgainst=len(lsCompanySame)-numFor
                    if numFor>numAgainst:
                        lsCompanySame.append(True)
                    else:
                        lsCompanySame.append(False)

        repOrgs = list(zip(lsAmtCompInt,lsRep0,lsCompanies0,lsCompanyStance,lsCompanySame,lsAmtComp,lsCompSector))        
        repOrgs.sort()
        repOrgs.reverse()

        #print 'HERE2'
        if len(naicsInd) > 0:
            nZip = list(zip([obj.rank for obj in naicsInd],naicsInd))
            nZip.sort()
            totalAmt,naicsInd = list(zip(*nZip))

        #print 'HERE3'
        t = loader.get_template('votes/one_vote_refined.html')
        c = Context({'refURL':ref_url,'vote':vote,'voters':biPartisan,'repOrgs':repOrgs,'pviReportRep':pviReportRep,'pviReportDem':pviReportDem,'repContr':repContr,'naicsInd':naicsInd,'relComm':relComm,'predElect':predElection})
        return HttpResponse(t.render(c))
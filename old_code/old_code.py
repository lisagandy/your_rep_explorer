# def all_votes(request,session):
#     lsVoteDescript=[]
#     votes = Vote.objects.filter(bill__congress=session).order_by('dateVote','number')
#     
#     lsContr=[]
#     lsInd=[]
#     lsOther=[]
#     lsComm=[]
#     for vote in votes:
#         allVoters = []
#         try:
#          allVoters = [av.rep for av in AnomVoters.objects.get(vote=vote).demVoters.all()]
#         except Exception:
#             pass
# 
#         try:
#             allVoters.extend([av.rep for av in AnomVoters.objects.get(vote=vote).repVoters.all()])
#         except Exception:
#             pass
#         
#         hasContr=False
#         if RepContributionReport.objects.filter(rep__in=allVoters,vote=vote).count() > 0:
#             hasContr=True
#             
#         hasInd=False
#         if NAICSIndustryReport.objects.filter(rep__in=allVoters,vote=vote).count() > 0:
#             hasInd=True
#     
#         hasOther=False
#         if PredElectionReport.objects.filter(predElection__rep__in=allVoters,vote=vote).count() > 0:
#             hasOther=True
#         
#         hasComm=False
#         if ChairCommitteeReport.objects.filter(rep__in=allVoters,vote=vote).count() > 0:
#             hasComm=True
#         
#         lsContr.append(hasContr)
#         lsInd.append(hasInd)
#         lsOther.append(hasOther)
#         lsComm.append(hasCommittee)
#     t = loader.get_template('votes/all_votes.xml')
#     c = Context({'votes':zip(votes,lsContr,lsInd,lsOther,lsComm)})
#     return HttpResponse(t.render(c),mimetype="application/xml")


# def load_vote(request,session,bill_prefix,bill_number,vote_number):
#     vote = Vote.objects.filter(bill__congress__number=session,bill__prefix=bill_prefix,bill__number=bill_number,number=vote_number)[0]
#     allVoters = []
#     try:
#      allVoters = [av for av in AnomVoters.objects.get(vote=vote).demVoters.all()]
#     
#     except Exception:
#         pass
#     
#     
#     try:
#         allVoters.extend([av for av in AnomVoters.objects.get(vote=vote).repVoters.all()])
#     except Exception:
#         pass
#         
#     biPartisan = []
#     predElection=[]
#     relComm = []
#     naicsInd = []
#     repContr = []
#     for av in allVoters:
#         voter=av.rep
#         try:
#             biPartisan.append(RepWithPartyReport.objects.get(vote=vote,repWithParty__rep=voter))
#         except Exception,ex:
#             print ex
#             biPartisan.append(None)
#     
#         try:
#             predElection.append(PredElectionReport.objects.get(vote=vote,predElection__rep=voter))
#         except Exception,ex:
#             print ex
#             predElection.append(None)
#             
#         try:
#             relComm.append(ChairCommitteeReport.objects.get(vote=vote,rep=voter))
#         except Exception,ex:
#             print ex
#             relComm.append(None)
#         
#         try:
#             naicsInd.append(NAICSIndustryReport.objects.get(vote=vote,rep=voter))
#         except Exception,ex:
#             print ex
#             naicsInd.append(None)
#         
#         
#         rcObjs = RepContributionReport.objects.filter(vote=vote,rep=voter)
#         if rcObjs.count() > 0:
#             repContr.append(rcObjs)
#         else:
#             repContr.append(None)
#         
#     
#     t = loader.get_template('votes/one_vote.xml')
#     c = Context({'vote':vote,'voters':zip(allVoters,biPartisan,predElection,relComm,naicsInd,repContr)})
#     return HttpResponse(t.render(c),mimetype="application/xml")


urlpatterns = patterns('',
    # Example:
    # (r'^ccu_beta/', include('ccu_beta.foo.urls')),
    #(r'^votes/session=(?P<session>\d+)&bill_prefix=(?P<bill_prefix>[a-z]+)&bill_number=(?P<bill_number>\d+)&vote_number=(?P<vote_number>\d+)$', 'ccu_gen_beta.views.load_vote'),
    # Uncomment the admin/doc line below and add 'django.contrib.admindocs' 
    # to INSTALLED_APPS to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),
    #(r'^votes/(?P<session>\d+)', 'ccu_gen_beta.views.all_votes'),
    (r'^votes/(?P<session>\d+)', 'ccu_gen_beta.views.all_votes_internal'),
    #(r'^reports/(?P<session>\d+)','ccu_gen_beta.views.reports'),
    (r'^reports/session=(?P<session>\d+)&bill_prefix=(?P<bill_prefix>[a-z]+)&bill_number=(?P<bill_number>\d+)&vote_number=(?P<vote_number>\d+)$', 'ccu_gen_beta.views.load_report'),
    # Uncomment the next line to enable the admin:
    (r'^admin/', include(admin.site.urls)),
)

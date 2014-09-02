from your_rep_explorer.ccu_gen_beta.models import *
from django.contrib import admin

class AnomVoters(admin.ModelAdmin):
	list_display=["vote","demVoters","repVoters"]

class CongressAdmin(admin.ModelAdmin):   
    list_display = ['number','beginDate','endDate']

class StateAdmin(admin.ModelAdmin):
    list_display = ['name','abbrev']
    search_fields = ['name','abbrev']    
    
class DistrictAdmin(admin.ModelAdmin):
    list_display = ['state','districtNum']
    search_fields = ['districtNum','state__name']

class StatePopAdmin(admin.ModelAdmin):
    list_display = ['state','pop','date']
    search_fields = ['state__name']

class StatePVIAdmin(admin.ModelAdmin):
    list_display = ['state','demCook','scoreCook','year']
    search_fields = ['state__name']

class DistrictPVIAdmin(admin.ModelAdmin):
    list_display = ['district','demCook','scoreCook','year']
    search_fields = ['district__state__name','district__districtNum']
 
class JonesTopicAdmin(admin.ModelAdmin):
    list_display = ['name','code']
    search_fields = ['name','code']

class JonesSubTopicAdmin(admin.ModelAdmin):
    list_display = ['name','topic','descript','code']
    search_fields = ['name','descript','code'] 

class MapLightSectorAdmin(admin.ModelAdmin):
    list_display = ['name','code']

class MapLightIndustryAdmin(admin.ModelAdmin):
    list_display = ['name','sector']
    search_fields = ['name']

class MapLightBusinessAdmin(admin.ModelAdmin):
    list_display = ['name','mlID','industry']
    search_fields = ['name','industry__sector__name','mlID']

class RepAdmin(admin.ModelAdmin):
    list_display = ('congress','lastName','firstName','state','district','party','senator','senatorClass','swornInDate','endDate')#'repID','repGovTrackID',)
    search_fields = ('lastName','senator','party','repGovTrackID')    

class RepContributionAdmin(admin.ModelAdmin):
    list_display = ['rep','rbID','dateContr','contribName','mlBusiness','isPAC']
    search_fields = ['rep__lastName','contribName','mlBusiness__name']

class NAICS_IndustryAdmin(admin.ModelAdmin):
    list_display = ['code','name','mlDirectMapping']
    search_fields = ['name']

# class NAICS_LocaleAdmin(admin.ModelAdmin):
#     list_display = ['state','numEmployees','naicsIndustry','beginQuarter','beginYear','endQuarter','endYear']
#     search_fields = ['state__name','naicsIndustry__name']
#     

class NAICS_LocaleAdmin(admin.ModelAdmin):
        list_display = ['state','numEmployeesTotal','numEmployees','naicsIndustry','beginQuarter','beginYear','endQuarter','endYear']
        search_fields = ['state__name','naicsIndustry__name']    

class ElectionAdmin(admin.ModelAdmin):
    list_display = ['date','senateClass']

class PredElectionAdmin(admin.ModelAdmin):
    list_display = ['election','rep','pred','date']
    search_fields = ['rep__lastName']

class RepADAAdmin(admin.ModelAdmin):
    list_display = ['rep','adaScore','year']
    search_fields = ['rep__lastName']

class RepWithPartyAdmin(admin.ModelAdmin):
    list_display = ['rep','withPartyScore','congress']
    search_fields = ['rep__lastName']

class CommitteeAdmin(admin.ModelAdmin):
    #list_display = ['congress','name','code','typeComm','chair','rankingMember']
    list_display=['name']
    search_fields = ['name','congress__number']

class BillAdmin(admin.ModelAdmin):
    list_display = ['congress','billNum','senate','popularTitle']
    search_fields = ['billNum','popularTitle']

class OrgStanceAdmin(admin.ModelAdmin):
    list_display = ['org','dateStance','against']
    search_fields = ['org__orgName']

class OrganizationAdmin(admin.ModelAdmin):
    list_display = ['orgID','orgName','mlBusiness']
    search_fields = ['orgID','orgName']

class AmendmentAdmin(admin.ModelAdmin):
    list_display = ['bill','number','purpose','description','offeredDate']
    search_fields = ['bill__number','number','purpose']

class VoteTypeAdmin(admin.ModelAdmin):
    list_display = ['voteType']

class VoteAdmin(admin.ModelAdmin):
    list_display = ['bill','number','dateVote','bill','amendment','voteType','result','senateVote']
    search_fields = ['bill__number','number']

class BillSubjectAdmin(admin.ModelAdmin):
    list_display = ['name','descript']
    search_fields = ['name']



admin.site.register(BillSubject,BillSubjectAdmin)
admin.site.register(OrgStance,OrgStanceAdmin)
admin.site.register(Vote,VoteAdmin)
admin.site.register(VoteType,VoteTypeAdmin)    
admin.site.register(Amendment,AmendmentAdmin)    
admin.site.register(Organization,OrganizationAdmin)
admin.site.register(Congress,CongressAdmin)
admin.site.register(State,StateAdmin)
admin.site.register(District,DistrictAdmin)
admin.site.register(StatePop,StatePopAdmin)
admin.site.register(StatePVI,StatePVIAdmin)
admin.site.register(DistrictPVI,DistrictPVIAdmin)
admin.site.register(JonesTopic,JonesTopicAdmin)
admin.site.register(JonesSubTopic,JonesSubTopicAdmin)
admin.site.register(MapLightSector,MapLightSectorAdmin)
admin.site.register(MapLightIndustry,MapLightIndustryAdmin)
admin.site.register(MapLightBusiness,MapLightBusinessAdmin)
admin.site.register(Rep,RepAdmin)
admin.site.register(RepContribution,RepContributionAdmin)
admin.site.register(NAICS_Industry,NAICS_IndustryAdmin)
admin.site.register(NAICS_Locale2,NAICS_LocaleAdmin)
admin.site.register(Election,ElectionAdmin)
admin.site.register(PredElection,PredElectionAdmin)
admin.site.register(RepADA,RepADAAdmin)
admin.site.register(RepWithParty,RepWithPartyAdmin)
admin.site.register(Committee,CommitteeAdmin)
admin.site.register(Bill,BillAdmin)
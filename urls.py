from django.conf.urls.defaults import *
import settings

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Example:
    # (r'^ccu_beta/', include('ccu_beta.foo.urls')),
    (r'^votes_xml/(?P<session>\d+)','ccu_gen_beta.views.all_votes_xml'),
    (r'^votes/xml=(?P<xml>\S+)&session=(?P<session>\d+)&bill_prefix=(?P<bill_prefix>[a-z]+)&bill_number=(?P<bill_number>\d+)&vote_number=(?P<vote_number>\d+)$', 'ccu_gen_beta.views.load_vote_xml'),
    
    (r'^votes/refined=True&session=(?P<session>\d+)&bill_prefix=(?P<bill_prefix>[a-z]+)&bill_number=(?P<bill_number>\d+)&vote_number=(?P<vote_number>\d+)$', 'ccu_gen_beta.views.load_vote_refined'),
    #(r'^votes/session=(?P<session>\d+)&bill_prefix=(?P<bill_prefix>[a-z]+)&bill_number=(?P<bill_number>\d+)&vote_number=(?P<vote_number>\d+)$', 'ccu_gen_beta.views.load_vote'),
    
    (r'^loadVotesContr/(?P<date>\S+)&(?P<sectorID>\S+)&(?P<indID>\S+)&(?P<busID>\S+)&(?P<senatorIDS>\S+)', 'ccu_gen_beta.views.load_votes_contr'),
    (r'^loadVotesTopic/(?P<date>\S+)&(?P<topicID>\S+)&(?P<subtopicID>\S+)&(?P<senatorIDS>\S+)', 'ccu_gen_beta.views.load_votes_topic'),
    (r'^loadVotesSenator/(?P<date>\S+)&(?P<stateName>\S+)&(?P<senatorIDS>\S+)', 'ccu_gen_beta.views.load_votes_senator'),
    (r'^popSelectBoxesBusinesses/(?P<date>\S+)&(?P<indID>\S+)', 'ccu_gen_beta.views.pop_select_boxes_business'),
    (r'^popSelectBoxesIndustry/(?P<date>\S+)&(?P<sectorID>\S+)', 'ccu_gen_beta.views.pop_select_boxes_industry'),
    (r'^popSelectBoxesSector/(?P<date>\S+)', 'ccu_gen_beta.views.pop_select_boxes_sector'),
    (r'^popSelectBoxesTopic/(?P<date>\S+)&(?P<topicID>\S+)', 'ccu_gen_beta.views.pop_select_boxes_topic'),
    (r'^popSelectBoxesSubtopic/(?P<date>\S+)&(?P<topicID>\S+)&(?P<subtopicID>\S+)', 'ccu_gen_beta.views.pop_select_boxes_subtopic'),
    (r'^popSelectBoxesState/(?P<date>\S+)&(?P<state>\S+)', 'ccu_gen_beta.views.pop_select_boxes_state'),
    (r'^popSelectBoxes/(?P<date>\S+)', 'ccu_gen_beta.views.pop_select_boxes'),
    (r'^demo111_house/?', 'ccu_gen_beta.views.all_votes111_house'),
    (r'^demo_house/?', 'ccu_gen_beta.views.all_votes112_house'),
    (r'^demo111/?', 'ccu_gen_beta.views.all_votes111_senate'),
    (r'^demo/?', 'ccu_gen_beta.views.all_votes112_senate'),
    #(r'^votes/(?P<session>\d+)', 'ccu_gen_beta.views.all_votes'),
    (r'^choose_votes_senator/?','ccu_gen_beta.views.choose_votes_senator'),
    (r'^choose_votes2/?','ccu_gen_beta.views.choose_votes2'),
    (r'^choose_votes/?','ccu_gen_beta.views.choose_votes'),
    (r'^about/?','ccu_gen_beta.views.about'),
    #(r'^rep_trial/(?P<repID>\S+)','ccu_gen_beta.views.rep'),
    (r'^ccu_api/?','ccu_gen_beta.views.ccu_api'), 
    (r'^admin/?', include(admin.site.urls)),
    
)

urlpatterns += patterns('',
    (r'^static/(?P<path>.*)$', 'django.views.static.serve',  
     {'document_root':     settings.MEDIA_ROOT}),
)

# urlpatterns += patterns('',(r'^/?','ccu_gen_beta.views.all_votes111'))
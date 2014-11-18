import pyUtilities as pyU
from datetime import date
import json as simplejson
from experiment.cosineTest import *
from ccu_gen_beta.models import *
import numpy
from decimal import Decimal
from paths import *


ref_url = "127.0.0.1:8000"

dStopWordTopic = {}


stateAbbrevs = {"WA": "WASHINGTON", "VA": "VIRGINIA", "DE": "DELAWARE", "DC": "DISTRICT OF COLUMBIA", "WI": "WISCONSIN", "WV": "WEST VIRGINIA", "HI": "HAWAII", "AE": "Armed Forces Middle East", "FL": "FLORIDA", "FM": "FEDERATED STATES OF MICRONESIA", "WY": "WYOMING", "NH": "NEW HAMPSHIRE", "NJ": "NEW JERSEY", "NM": "NEW MEXICO", "TX": "TEXAS", "LA": "LOUISIANA", "NC": "NORTH CAROLINA", "ND": "NORTH DAKOTA", "NE": "NEBRASKA", "TN": "TENNESSEE", "NY": "NEW YORK", "PA": "PENNSYLVANIA", "CA": "CALIFORNIA", "NV": "NEVADA", "AA": "Armed Forces Americas", "PW": "PALAU", "GU": "GUAM", "CO": "COLORADO", "VI": "VIRGIN ISLANDS", "AK": "ALASKA", "AL": "ALABAMA", "AP": "Armed Forces Pacific", "AS": "AMERICAN SAMOA", "AR": "ARKANSAS", "VT": "VERMONT", "IL": "ILLINOIS", "GA": "GEORGIA", "IN": "INDIANA", "IA": "IOWA", "OK": "OKLAHOMA", "AZ": "ARIZONA", "ID": "IDAHO", "CT": "CONNECTICUT", "ME": "MAINE", "MD": "MARYLAND", "MA": "MASSACHUSETTS", "OH": "OHIO", "UT": "UTAH", "MO": "MISSOURI", "MN": "MINNESOTA", "MI": "MICHIGAN", "MH": "MARSHALL ISLANDS", "RI": "RHODE ISLAND", "KS": "KANSAS", "MT": "MONTANA", "MP": "NORTHERN MARIANA ISLANDS", "MS": "MISSISSIPPI", "PR": "PUERTO RICO", "SC": "SOUTH CAROLINA", "KY": "KENTUCKY", "OR": "OREGON", "SD": "SOUTH DAKOTA"}

#Created on 6/1/2011
districts = {'GUAM':0,'ALABAMA':7,'ALASKA':0,"AMERICAN SAMOA":0,'ARIZONA':9,'ARKANSAS':4,'CALIFORNIA':53,'COLORADO':7,'CONNECTICUT':5,'DELAWARE':0,'DISTRICT OF COLUMBIA':0,'FLORIDA':27,'GEORGIA':14,'HAWAII':2,'IDAHO':2,'ILLINOIS':19,'INDIANA':9,'IOWA':5,'KANSAS':4,'KENTUCKY':6,'LOUISIANA':7,'MAINE':2,'MARYLAND':8,'MASSACHUSETTS':10,'MICHIGAN':15,'MINNESOTA':8,'MISSISSIPPI':5,'MISSOURI':9,'MONTANA':0,'NEBRASKA':3,'NEVADA':3,'NEW HAMPSHIRE':2,'NEW JERSEY':13,'NEW MEXICO':3,'NEW YORK':29,'NORTH CAROLINA':13,'NORTH DAKOTA':0,'NORTHERN MARIANA ISLANDS':0,'OHIO':18,'OKLAHOMA':5,'OREGON':5,'PENNSYLVANIA':19,'PUERTO RICO':0,'RHODE ISLAND':2,'SOUTH CAROLINA':6,'SOUTH DAKOTA':0,'TENNESSEE':9,'TEXAS':36,'VIRGIN ISLANDS':0,'UTAH':4,'VERMONT':0,'VIRGINIA':11,'WASHINGTON':10,'WEST VIRGINIA':3,'WISCONSIN':8,'WYOMING':0,}

def convertMoney(value):
	return moneyfmt(Decimal(str(value)),curr='$')


def moneyfmt(value, places=2, curr='', sep=',', dp='.',
             pos='', neg='-', trailneg=''):
    """Convert Decimal to a money formatted string.

    places:  required number of places after the decimal point
    curr:    optional currency symbol before the sign (may be blank)
    sep:     optional grouping separator (comma, period, space, or blank)
    dp:      decimal point indicator (comma or period)
             only specify as blank when places is zero
    pos:     optional sign for positive numbers: '+', space or blank
    neg:     optional sign for negative numbers: '-', '(', space or blank
    trailneg:optional trailing minus indicator:  '-', ')', space or blank

    >>> d = Decimal('-1234567.8901')
    >>> moneyfmt(d, curr='$')
    '-$1,234,567.89'
    >>> moneyfmt(d, places=0, sep='.', dp='', neg='', trailneg='-')
    '1.234.568-'
    >>> moneyfmt(d, curr='$', neg='(', trailneg=')')
    '($1,234,567.89)'
    >>> moneyfmt(Decimal(123456789), sep=' ')
    '123 456 789.00'
    >>> moneyfmt(Decimal('-0.02'), neg='<', trailneg='>')
    '<0.02>'

    """
    q = Decimal(10) ** -places      # 2 places --> '0.01'
    sign, digits, exp = value.quantize(q).as_tuple()
    result = []
    digits = map(str, digits)
    build, next = result.append, digits.pop
    if sign:
        build(trailneg)
    for i in range(places):
        build(next() if digits else '0')
    build(dp)
    if not digits:
        build('0')
    i = 0
    while digits:
        build(next())
        i += 1
        if i == 3 and digits:
            i = 0
            build(sep)
    build(curr)
    build(neg if sign else pos)
    return ''.join(reversed(result))

def describeVoteSimple(vote):
    billTitle=""
    if vote.bill.popularTitle:
        billTitle = vote.bill.popularTitle
    else:
        try:
            billTitle = vote.bill.otherTitles.all()[0].title
        except Exception:
            pass

    strRet = '<h2><a href="http://127.0.0.1:8000/votes/refined=True&session=' + str(vote.bill.congress.number) + "&bill_prefix=" + str(vote.bill.prefix) + "&bill_number=" + str(vote.bill.number) + "&vote_number=" + str(vote.number) + '">Vote #%d on %s</a></h2>' % (vote.number,vote.dateVote.strftime("%B %d, %Y"))
    strRet += "A vote "
    if vote.question.lower().find('motion') > -1 and vote.question.lower().find('cloture')==-1:
        strRet += " to pass "
    elif vote.question.lower().find('cloture') > -1:
        strRet += " to end debate on "
    else:
        strRet += vote.question

    if vote.amendment:
        strRet += "Amendment %s to " % vote.amendment.number.upper()
    strRet += "Bill %s.%s: %s" % (vote.bill.prefix.upper(), vote.bill.number, billTitle)
    strRet+="<br>"

    strRunDown = "%d%% needed to pass, %d%% received" % (int(vote.percentNeeded*100),int(vote.percentGotten*100))
    if vote.percentGotten < vote.percentNeeded:
        strRet+="The vote <b>failed</b> (%s)<br>" % strRunDown
    else:
        strRet+="The vote <b>passed</b> (%s)<br>" % strRunDown

    try:
        if vote.amendment:
            subtopic = vote.amendment.subtopics.all()[0]
            subtopicStr = subtopic.topic.name
            if subtopic.name.find('eneral') == -1:
                subtopicStr+= ", %s" % subtopic.name

            strRet+="The amendment focuses on <b>%s</b><br>" % (subtopicStr)
        else:
            subtopic = vote.bill.subtopics.all()[0]
            subtopicStr = subtopic.topic.name
            if subtopic.name.find('eneral') == -1:
                subtopicStr+= ", %s" % subtopic.name
            strRet+="The bill focuses on <b>%s</b><br>" % (subtopicStr)
    except Exception:
        pass

    return strRet


#from your_rep_explorer.ccu_gen_beta.models import *
#print generateName(Rep.objects.get(congress__number=112,lastName='Adams'))
#assert 0

def describeVote(vote,typeDescript):
    billTitle=""
    if vote.bill.popularTitle:
        billTitle = vote.bill.popularTitle
    else:
        try:
            billTitle = vote.bill.otherTitles.all()[0].title
        except Exception:
            pass

    strRet = 'Congress #%d, Vote #%d on date %s\n' % (vote.bill.congress.number,vote.number,vote.dateVote)
    if vote.amendment:
        strRet += "<b>Amendment #%s</b> sponsored by %s\n" % (vote.amendment.number.upper(), generateName(vote.amendment.sponsor))
        strRet += '<b>Amendment Purpose:</b> %s\n' % vote.amendment.purpose
        if typeDescript=="topic":
            dTS = vote.amendment.groupedByTopic()
            lsTopics = dTS.keys()
            lsTopics.sort()
            if len(lsTopics) > 0:
                strRet+="<b>Amendment Topics: </b>"
                for topic in lsTopics:
                    strRet += "%s," % (topic.name.replace(',',' '))
                strRet=strRet[0:-1]
                strRet+='\n'

        strRet += '<b>Related Bill</b>: %s.%s: %s\n' % (vote.bill.prefix.upper(),vote.bill.number,billTitle)


    else:
        strRet += '<b>Bill %s.%s:</b> %s\n' % (vote.bill.prefix.upper(),vote.bill.number,billTitle)
        billDescript = vote.bill.twoPartSummary()[0].replace('\n','')
        #if len(billDescript.strip()) > 0:
            #strRet += "<b>Bill description:</b>%s...\n" % (billDescript)
        if typeDescript=="topic":
            dTS = vote.bill.groupedByTopic()
            lsTopics = dTS.keys()
            lsTopics.sort()
            if len(lsTopics) > 0:
                strRet+="<b>Bill Topics:</b>"
                for topic in lsTopics:
                    strRet += " %s," % (topic.name.replace(',',' '))
                strRet=strRet[0:-1]
                strRet+='\n'

    strRet += ' <b>Vote Question:</b> %s\n' % vote.question
    strRet += ' <b>Vote Result:</b> %s\n' % vote.result
    allVoters = getAllAnomVoters(vote)
    if not allVoters:
        strRet+= "WHY NO ANOM VOTERS???\n"
        return strRet
    strSenators = ', '.join([av.rep.officialName() for av in allVoters])
    strRet += ' <b>Senators Who Voted Against Party:</b> %s\n' % strSenators

    if typeDescript and typeDescript.find('contr') > -1:
        lsAll = []
        if typeDescript=="contrSector":
            rcs = RepContributionReport.objects.filter(vote=vote)
            for rc in rcs:
                if rc.mlBusiness.industry.sector.name not in lsAll:
                    lsAll.append(rc.mlBusiness.industry.sector.name)

        elif typeDescript=="contrInd":
            rcs = RepContributionReport.objects.filter(vote=vote)
            for rc in rcs:
                if rc.mlBusiness.industry.name not in lsAll:
                    lsAll.append(rc.mlBusiness.industry.name)


        elif typeDescript=="contrBus":
            rcs = RepContributionReport.objects.filter(vote=vote)
            lsBus = []
            for rc in rcs:
                if rc.mlBusiness.name not in lsAll:
                    lsAll.append(rc.mlBusiness.name)

        lsAll.sort()
        strRet += "<b>Contributions From: </b>"
        strRet += ', '.join(lsAll)
        strRet += "<br>"

    #strRet += '<a href="http://' + ref_url + '/votes/session=' + str(vote.bill.congress.number) + '&amp;bill_prefix=' + vote.bill.prefix + '&amp;bill_number=' + str(vote.bill.number) + '&amp;vote_number=' + str(vote.number) + '">View Full Report Here</a><br>'
    return strRet

def describeVoteHTML(vote,typeDescript=None):
    strRet = describeVote(vote,typeDescript).replace('\n','<br>')
    return strRet

def isOutlier(num,lsAllNums,only_high=False):
    lsAllNums.sort()
    median = numpy.median(lsAllNums)
    list1 = lsAllNums[0:int(len(lsAllNums)/2)]
    list2 = lsAllNums[int(len(lsAllNums)/2+0.5):]
    high_range = numpy.median(list2)
    low_range = numpy.median(list1)

    mean=numpy.mean(lsAllNums)
    z_index = abs(num-mean)/numpy.std(lsAllNums)
    if num < low_range and z_index > 3 and only_high==False:
        return True,'LOW'
    elif num > high_range and z_index > 3:
        return True,'HIGH'
    elif num > high_range:
        return True,"MILD HIGH"
    elif num < low_range and only_high==False:
        return True,"MILD LOW"
    return False,None


def isOutlierStats(num,pcStat):
    median = pcStat.median
    high_range = pcStat.high_range
    low_range = pcStat.low_range

    try:
        mean=pcStat.mean
        z_index = float(abs(num-pcStat.mean))/pcStat.std
    except Exception:
        z_index=0

    if num < median and z_index > 3:
        return True,'LOW'
    elif num > median and z_index > 3:
        return True,'HIGH'
    elif num > high_range:
        return True,"MILD HIGH"
    elif num < low_range:
        return True,"MILD LOW"
    return False,None

#from ccu_gen_beta.models import *
#print isOutlierStats(67,PercentWithPartyStats(high_range=100,low_range=100,mean=98,median=100,std=5.7))
# assert 0


def findJonesSubTopicPres(descript,lsTopic,score=0.09,sameAsLast=False):
    stopWordPerTopic = simplejson.loads(open(CCU_DATA_PATH + 'topics_stopwords.txt').read())
    ret = {}

    if not sameAsLast:
        clear()
        for topic in lsTopic:
            if not topic in dStopWordTopic:
                try:
                    stopWords = stopWordPerTopic[topic.name]
                except Exception:
                    pass

                for to in JonesSubTopic.objects.filter(topic=topic):
                    txt = to.name + ' ' + to.descript
                    for word in stopWords:
                         reI = re.compile('\W+' + word + '\W+',re.I)
                         '''complete words'''
                         txt = reI.sub(' ',txt)
                         reI = re.compile('\W+' + word + '\w+',re.I)
                         '''stemmed words'''
                         txt = reI.sub(' ',txt)
                    add_document(to.name,txt)
                    dStopWordTopic[to.name] = txt
            else:
                add_document(to.name,dStopWordTopic[to.name])

    tns = classify_document(descript)
    #tns2 = {}
    #for key,val in tns.items():
        #if val > 0:
            #tns2[key] = val
    #print tns2
    #print tns
    if tns.keys() == []:
        return tns

    tns = zip(tns.values(),tns.keys())
    tns.sort()
    tns.reverse()
    topic_score2,topic_name2 = zip(*tns)

    ret = {}
    for stopic_score,stopic_name in zip(topic_score2,topic_name2):
        if stopic_score > score:
            jst = JonesSubTopic.objects.filter(name=stopic_name)[0]
            if jst.topic in lsTopic:
                ret[jst] = stopic_score

    return ret

def findJonesSubTopicPresUniqueWords(descript,lsTopic,score=0.09,sameAsLast=False):
        ret = {}
        try:
            stopWordPerTopic = simplejson.loads(open(CCU_DATA_PATH + 'topics_stopwords.txt').read())
        except Exception:
            return

        if not sameAsLast:
            clear()
            for topic in lsTopic:
                if not topic in dStopWordTopic:
                    stopWords = stopWordPerTopic[topic.name]
                    for to in JonesSubTopic.objects.filter(topic=topic):
                        txt = to.name + ' ' + to.descript
                        for word in stopWords:
                             reI = re.compile('\W+' + word + '\W+',re.I)
                             '''complete words'''
                             txt = reI.sub(' ',txt)
                             reI = re.compile('\W+' + word + '\w+',re.I)
                             '''stemmed words'''
                             txt = reI.sub(' ',txt)
                        add_document_unique(to.name,txt)
                        dStopWordTopic[to.name] = txt
                else:
                    add_document_unique(to.name,dStopWordTopic[to.name])

        tns = classify_document_unique(descript)
        #tns2 = {}
        #for key,val in tns.items():
            #if val > 0:
                #tns2[key] = val
        #print tns2
        #print tns
        if tns.keys() == []:
            return tns

        tns = zip(tns.values(),tns.keys())
        tns.sort()
        tns.reverse()
        topic_score2,topic_name2 = zip(*tns)

        ret = {}
        for stopic_score,stopic_name in zip(topic_score2,topic_name2):
            if stopic_score > score:
                jst = JonesSubTopic.objects.filter(name=stopic_name)[0]
                if jst.topic in lsTopic:
                    ret[jst] = stopic_score

        return ret



def findJonesSubTopicPresTitleOnly(descript,lsTopic,score=0.09,sameAsLast=False):
        stopWordPerTopic = simplejson.loads(open(CCU_DATA_PATH + 'topics_stopwords.txt').read())
        ret = {}

        if not sameAsLast:
             clear()
             for topic in lsTopic:
                if not topic in dStopWordTopic:
                    stopWords = stopWordPerTopic[topic.name]
                    for to in JonesSubTopic.objects.filter(topic=topic):
                        txt = to.name + ' ' + to.descript
                        for word in stopWords:
                             reI = re.compile('\W+' + word + '\W+',re.I)
                             '''complete words'''
                             txt = reI.sub(' ',txt)
                             reI = re.compile('\W+' + word + '\w+',re.I)
                             '''stemmed words'''
                             txt = reI.sub(' ',txt)
                        add_document(to.name,txt)
                        dStopWordTopic[to.name] = txt
                else:
                    add_document(to.name,dStopWordTopic[to.name])

        tns = classify_document(descript)
        tns2 = {}
        for key,val in tns.items():
            if val > 0:
                tns2[key] = val
        #print tns2

        tns = zip(tns.values(),tns.keys())
        tns.sort()
        tns.reverse()
        topic_score2,topic_name2 = zip(*tns)

        ret = {}
        for stopic_score,stopic_name in zip(topic_score2,topic_name2):
            if stopic_score > score:
                jst = JonesSubTopic.objects.filter(name=stopic_name)[0]
                if jst.topic in lsTopic:
                    ret[jst] = stopic_score

        return ret



'''May 22,1980'''
def createDate2(dateStr):
    month = pyU.numberMonth(dateStr.split(',')[0].split()[0])
    year = int(dateStr.split(',')[-1])
    day = int(dateStr.split(',')[0].split()[1])
    return date(year,month,day)

'''2009-09-19'''
def createDate3(dateStr):
    year = int(dateStr.split('-')[0])
    month = int(dateStr.split('-')[1])
    day = int(dateStr.split('-')[2])
    return date(year,month,day)

'''2009, April 23'''
def createDate4(dateStr):
    year = int(dateStr.split(',')[0])
    month = pyU.numberMonth(dateStr.split(',')[1].split()[0])
    day = int(dateStr.split()[-1])
    return date(year,month,day)

'''05-02-2011'''
def createDate5(dateStr):
    year = int(dateStr.split('-')[2])
    month = int(dateStr.split('-')[0])
    day = int(dateStr.split('-')[1])
    return date(year,month,day)

if __name__=="__main__":
    print isPVIOutlier(Rep.objects.filter(congress__number=112,lastName='Stabenow')[0],Vote.objects.filter(bill__congress__number=112)[0])
    assert 0
    print isPVIOutlier(Rep.objects.filter(congress__number=112,senator=True,state__name='UTAH')[0],Vote.objects.filter(bill__congress__number=112)[0])
    print isPVIOutlier(Rep.objects.filter(congress__number=112,lastName='Brown',firstName='Scott')[0],Vote.objects.filter(bill__congress__number=112)[0])
    print isPVIOutlier(Rep.objects.filter(congress__number=112,lastName='Hutchison',firstName='Kay')[0],Vote.objects.filter(bill__congress__number=112)[0])

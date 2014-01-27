import csv
from ccu_gen_beta.models import *
from pyStemmer import sStem
from pyUtilities import bIsStopWord,removePunctuation,stripExtraSpaces
from math import log
import re
import simplejson
from cosineTest import *
import scipy.stats
from paths import *


def _clean_text(text):
    reNum = re.compile('\d+')
    text = ' '.join([w for w in text.split()]) #if not bIsStopWord(w)])
    text = sStem(text)
    text = re.sub(reNum,' ',text)
    return stripExtraSpaces(removePunctuation(text.lower()))

def makeFreqDict(lsWords):
    dRet = {}
    for word in lsWords:
        if word not in dRet:
            dRet[word] = 1
        else:
            dRet[word] +=1
    return dRet

def tf(word,dWords):
    wordFreq = dWords[word]
    sumWords = sum([val for val in dWords.values()])
    return wordFreq/float(sumWords)

def idf(word,dDocs):
    totalDocs = len(dDocs.keys())
    totalDocsOccur = 0
    for name,words in dDocs.items():
        if word in words.keys():
            totalDocsOccur+=1
    return log(totalDocs/totalDocsOccur)


def createTFIDFJones(dDocs):
    dDocFreq = {}
    for docName in dDocs.keys():
        dDocFreq[docName] = {}
    
    for docName,words in dDocs.items():
        for word in words:
            #print word
            #print words
            tfNum = tf(word,words) 
            #print tfNum
            idfNum = idf(word,dDocs)
            #print idfNum
            dDocFreq[docName][word] = tfNum * idfNum
    return dDocFreq
 
def calculateTFIDFTopics():
    from pyStemmer import sStem
    dDocs = {}
    for index,topic in enumerate(JonesTopic.objects.all()):
        txt = ""
        for subtopic in JonesSubTopic.objects.filter(topic=topic):
            txt= txt + ' ' + _clean_text(subtopic.name + ' ' + subtopic.descript)
        
        dDocs[topic.name] = makeFreqDict(txt.split())
    return createTFIDFJones(dDocs)


#d['topicname'] = {'word':'score','word':'score'}
def calculateCutoffs(dAll):
    dCutoffs = {}
    for topic in dAll.keys():
        scores = dAll[topic].values()
        scores.sort()
        scores.sort()
        dCutoffs[topic] = [scipy.stats.scoreatpercentile(scores,25),scipy.stats.scoreatpercentile(scores,75)]
    return dCutoffs    

def createJonesStopWordsQuartiles():
    dAll = calculateTFIDFTopics()
    dCutoffs = calculateCutoffs(dAll)
    
    dStopWords = {}
    for docName in dAll.keys():
        if docName in dCutoffs.keys():
            dStopWords[docName] = []
          
    for docName,words in dAll.items():
        for word,score in words.items():
            if words[word] <= dCutoffs[docName][0]: #or words[word] > dCutoffs[docName][1]:
                dStopWords[docName].append(word)
  
    open(CCU_DATA_PATH + 'topics_stopwords.txt','w').write(simplejson.dumps(dStopWords))
  
if __name__ == '__main__':
    createJonesStopWordsQuartiles()
    
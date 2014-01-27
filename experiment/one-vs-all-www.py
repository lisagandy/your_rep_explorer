from pyStemmer import sStem
import csv
import re
from pyUtilities import bIsStopWord,removePunctuation,stripExtraSpaces
from math import log
from ccu_gen_beta.models import *
import os

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

def tf(wordMatch,allWords):
    i=0
    for word in allWords:
        if word==wordMatch:
            i+=1
    return i
    
def idf(word,dIDF,dDocs):
    totalDocs = len(dDocs.keys())
    return log(totalDocs/float(dIDF[word]))

def createIDFDictionary(dDocs):
    dWords = {}
    for docName,words in dDocs.items():
        lsTrack = []
        for word in words:
            if word not in lsTrack: #only count word once per document
                if word not in dWords:
                    dWords[word] = 1 #first occurrence
                else:
                    dWords[word] +=1 #occurred in doc
                lsTrack.append(word)
    
    return dWords
    
def createTFIDF(dDocs):
    dDocFreq = {}
    #docName is a right now
    for docName in dDocs.keys():
        dDocFreq[docName] = {}
    
    print 'creating IDF Dictionary'
    dIDF = createIDFDictionary(dDocs)
    
    print 'analyzing all words'
    for docName,words in dDocs.items():
        if docName % 1000 == 0:
            print docName
        for word in words:
            tfNum = tf(word,words) 
            idfNum = idf(word,dIDF,dDocs)
            dDocFreq[docName][word] = tfNum * idfNum
    return dDocFreq,dIDF.keys()
 
def findAllTFIDF():
    path = "/Users/lisagandy/Desktop/www2012/bills_topics_merge/"
    fileNames = ['%sall_data_no_duplicates.csv' % path]
    i = 0
    dBills = {}
    for fileName in fileNames:
        print fileName
        f = open(fileName,'rU')        
        for row in csv.DictReader(f):
            txt = row['Title']
            dBills[i] = _clean_text(txt).split()
            i+=1
    
    dDocFreq,lsAllWords = createTFIDF(dBills)
    return dDocFreq,lsAllWords

def createTrainingFiles():
    # dDocFreq,lsAllWords = findAllTFIDF()
    #     f = open('/Users/lisagandy/Desktop/www2012/dDocFreq.txt','w')
    #     strNew = simplejson.dumps(dDocFreq)
    #     f.write(strNew)
    #     f.close()
    #     f = open('/Users/lisagandy/Desktop/www2012/lsAllWords.txt','w')
    #     strNew = simplejson.dumps(lsAllWords)
    #     f.write(strNew)
    #     f.close()

    dDocFreq = simplejson.load(open('/Users/lisagandy/Desktop/www2012/dDocFreq.txt'))
    lsAllWords = simplejson.load(open('/Users/lisagandy/Desktop/www2012/lsAllWords.txt'))
    # print len(lsAllWords)
    #    fAllWords = open('/Users/lisagandy/Desktop/lookup_table.txt','w')
    #    for index,word in enumerate(lsAllWords):
    #        fAllWords.write('%d ' % index)
    #        fAllWords.write(word + '\n')
    #    fAllWords.close()
    #    assert 0
    
    trainPath = '/Users/lisagandy/Desktop/one_vs_all_www/'
    for topic in JonesTopic.objects.all():
          trainDir = trainPath + str(topic.code)
          os.popen('mkdir %s' % trainDir)
          fOpenTFIDF = open(trainDir + '/%s.txt' % topic.code,'w')
          print trainDir + '/%s.txt' % topic.code
          
          path = "/Users/lisagandy/Desktop/www2012/bills_topics_merge/"
          fileNames = ['%sall_data_no_duplicates.csv' % path]
          i = 0
          for fileName in fileNames:
              f = open(fileName,'rU')
              for row in csv.DictReader(f):
                  classif = int(row['Major'])
                  if classif != topic.code:
                      classif = 0
                      
                  lineOut = str(classif)
                  words = _clean_text(row['Title']).split()
                  lsTempWords = []
                  lsTempScores = []
                  lsTrack = []
                  for word in words:
                      if word in lsTrack:
                          continue
                      lsTempWords.append(lsAllWords.index(word))
                      lsTempScores.append(dDocFreq[str(i)][word])
                      lsTrack.append(word)
                      
                  lsTemp = zip(lsTempWords,lsTempScores)
                  lsTemp.sort()
                  lsTempWords,lsTempScores = zip(*lsTemp)
                  for j in range(0,len(lsTempWords)):
                      lineOut = lineOut + " " + "%s:%s" % (str(lsTempWords[j]),str(lsTempScores[j]))
                      
                  
                  fOpenTFIDF.write(lineOut + '\n')
                  i+=1
          fOpenTFIDF.close()
          command = 'svm-scale -l 0 -s %s %s' % (trainDir + '/range.txt',trainDir + '/%s.txt' % topic.code)
          print command
          txt = os.popen(command).read()
          scaledFileName = trainDir + '/%s_scaled.txt' % topic.code
          f = open(scaledFileName,'w')
          f.write(txt)
          f.close()
    
    for topic in JonesTopic.objects.all():
            subtopics = JonesSubTopic.objects.filter(topic=topic)
            for subtopic in subtopics:
                trainDir = trainPath + str(topic.code) + '/%s/' % str(subtopic.code)
                print trainDir
                os.popen('mkdir %s' % trainDir)
                fOpen = open(trainDir + '%s.txt' % (subtopic.code),'w')
                print trainDir + '%s.txt' % (subtopic.code)

                path = "/Users/lisagandy/Desktop/www2012/bills_topics_merge/"
                fileNames = ['%sall_data_no_duplicates.csv' % path]
                i = 0
                for fileName in fileNames:
                    f = open(fileName,'rU')
                    for row in csv.DictReader(f):
                        classif = int(row['Major'])
                        if classif != topic.code:
                            i=i+1
                            continue
                        
                        subclassif = int(row['Subtopic'])
                        if subclassif != subtopic.code:
                            subclassif = 0
                            
                        lineOut = str(subclassif)
                        words = _clean_text(row['Title']).split()
                        lsTempWords = []
                        lsTempScores = []
                        lsTrack = []
                        for word in words:
                            if word in lsTrack:
                                continue
                            lsTempWords.append(lsAllWords.index(word))
                            lsTempScores.append(dDocFreq[str(i)][word])
                            lsTrack.append(word)
                            
                        lsTemp = zip(lsTempWords,lsTempScores)
                        lsTemp.sort()
                        lsTempWords,lsTempScores = zip(*lsTemp)
                        for j in range(0,len(lsTempWords)):
                            lineOut = lineOut + " " + "%s:%s" % (str(lsTempWords[j]),str(lsTempScores[j]))
                        
                        fOpen.write(lineOut + '\n')
                        i+=1
                fOpen.close()        
                command = 'svm-scale -l 0 -s %s %s' % (trainDir + '/range.txt',trainDir + '/%s.txt' % subtopic.code)
                print command
                txt = os.popen(command).read()
                scaledFileName = trainDir + '/%s_scaled.txt' % subtopic.code
                f = open(scaledFileName,'w')
                f.write(txt)
                f.close()       
                
        
        
        
        

if __name__ == '__main__':
    createTrainingFiles()
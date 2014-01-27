import csv
import pyUtilities as pyU
import simplejson
from pyStemmer import *
import os
from ccu_gen_beta.models import *

dJT = {}
dJT[1] = JonesTopic.objects.filter(name__icontains='Macro')[0]
dJT[2] = JonesTopic.objects.filter(name__icontains='Civil Rights')[0]
dJT[3] = JonesTopic.objects.filter(name__icontains='Health')[0]
dJT[4] = JonesTopic.objects.filter(name__icontains='Agriculture')[0]
dJT[5] = JonesTopic.objects.filter(name__icontains='Labor')[0]
dJT[6] = JonesTopic.objects.filter(name__icontains='Education')[0]
dJT[7] = JonesTopic.objects.filter(name__icontains='Environment')[0]
dJT[8] = JonesTopic.objects.filter(name__icontains='Energy')[0]
dJT[10] = JonesTopic.objects.filter(name__icontains='Transportation')[0]
dJT[12] = JonesTopic.objects.filter(name__icontains='Law')[0]
dJT[13] = JonesTopic.objects.filter(name__icontains='Social')[0]
dJT[14] = JonesTopic.objects.filter(name__icontains='Community')[0]
dJT[15] = JonesTopic.objects.filter(name__icontains='Banking')[0]
dJT[16] = JonesTopic.objects.filter(name__icontains='Defense')[0]
dJT[17] = JonesTopic.objects.filter(name__icontains='Space')[0]
dJT[18] = JonesTopic.objects.filter(name__icontains='Foreign Trade')[0]
dJT[19] = JonesTopic.objects.filter(name__icontains='International')[0]
dJT[20] = JonesTopic.objects.filter(name__icontains='Government')[0]
dJT[21] = JonesTopic.objects.filter(name__icontains='Public')[0]

dDir = {}
dDir[1] = 'macro'
dDir[2] = 'civil'
dDir[3] = 'health'
dDir[4] = 'agri'
dDir[5] = 'labor'
dDir[6] = 'ed'
dDir[7] = 'env'
dDir[8] = 'energy'
dDir[10] = 'trans'
dDir[12] = 'law'
dDir[13] = 'soc'
dDir[14] = 'comm'
dDir[15] = 'bank'
dDir[16] = 'def'
dDir[17] = 'space'
dDir[18] = 'for'
dDir[19] = 'int'
dDir[20] = 'gov'
dDir[21] = 'pub'

modelDir = '/Users/lisagandy/Desktop/classif/'

#work on this a bit more, 110 and 199 not represented
subTopicCodesMacro = [0,100,101,103,104,105,107,108,110,199]
topicCodeMacro = 1

subTopicCodesCivil = [0,200,201,202,204,205,206,207,208,209,299]
topicCodeCivil = 2

subTopicCodesHealth = [0,300,301,302,321,322,323,324,325,331,332,333,334,335,336,341,342,343,344,398,399]
topicCodeHealth = 3

subTopicCodesAgri = [0,400,401,402,403,404,405,498,499]
topicCodeAgri = 4

subTopicCodesLabor = [0,500,501,502,503,504,505,506,508,529,530,599]
topicCodeLabor = 5

subTopicCodesEd = [0,600,601,602,603,604,606,607,609,698,699]
topicCodeEd = 6

subTopicCodesEnv = [0,700,701,703,704,705,707,708,709,710,711,798,799]
topicCodeEnv = 7

subTopicCodesEnergy = [0,800,801,802,803,805,806,807,898,899]
topicCodeEnergy = 8

subTopicCodesTrans = [0,1000,1001,1002,1003,1005,1006,1007,1010,1098,1099]
topicCodeTrans = 10

subTopicCodesLaw = [0,1200,1201,1202,1203,1204,1205,1206,1207,1208,1209,1210,1211,1299]
topicCodeLaw = 12

subTopicCodesSoc = [0,1300,1301,1302,1303,1304,1305,1399]
topicCodeSoc = 13

subTopicCodesComm = [0,1400,1401,1403,1404,1405,1406,1407,1408,1409,1410,1499]
topicCodeComm = 14

subTopicCodesBank = [0,1500,1501,1502,1504,1505,1507,1520,1521,1522,1523,1524,1525,1526,1599]
topicCodeBank = 15

subTopicCodesDef = [0,1600,1602,1603,1604,1605,1606,1608,1609,1610,1611,1612,1614,1615,1616,1617,1619,1620,1698,1699]
topicCodeDef = 16

subTopicCodesSpace = [0,1700,1701,1704,1705,1706,1707,1708,1709,1798,1799]
topicCodeSpace = 17

subTopicCodesFor = [0,1800,1802,1803,1804,1806,1807,1808,1899]
topicCodeFor = 18

#missing 1912
subTopicCodesInt = [0,1900,1901,1902,1905,1906,1907,1908,1909,1910,1911,1912,1914,1915,1919,1920,1925,1926,1927,1929,1999]
topicCodeInt = 19

#missing 2010
subTopicCodesGov = [0,2000,2001,2002,2003,2004,2005,2006,2007,2008,2009,2010,2011,2012,2013,2014,2015,2030,2099]
topicCodeGov = 20

subTopicCodesPub = [0,2100,2101,2102,2103,2104,2105,2199]
topicCodePub = 21

def train(lsFiles,topicNum,lsSubTopics,modelDir):
    
    #---------BUILD TRAINING DATA-----------#
    trainFile = '%s/train.txt' % modelDir
    scaledTrain = '%s/scale_train.txt' % modelDir
    rangeFile = '%s/range_train.txt' % modelDir
    wordFile = '%s/words_bigram.txt' % modelDir
    build_file(lsFiles,trainFile,wordFile,topicNum,lsSubTopics)
    
    #finished writing training file, scale...
    scale_file(trainFile,scaledTrain,rangeFile,True)
    
    #build training model
    modelFile = '%s/m.model' % modelDir
    train_file(scaledTrain,modelFile)
    return modelFile,wordFile,rangeFile


def train_file(trainFile,modelFile):
    command = 'svm-train -t 0 %s %s' % (trainFile,modelFile)
    os.popen(command)

def scale_file(inFileName,scaledFileName,rangeFile,train=True):
    if train:
        command = 'svm-scale -l 0 -s %s %s' % (rangeFile,inFileName)
    else:
        command = 'svm-scale -l 0 -r %s %s' % (rangeFile,inFileName)
    #print command
    txt = os.popen(command).read()
    f = open(scaledFileName,'w')
    f.write(txt)
    f.close()
    
       
def writeFile(descript,lsAllWords,fTrain,classif):
    descript = pyU.removePunctuation(descript)
    descript = pyU.sStripStopWordsAll(descript)
    fTrain.write(str(classif)+' ')
    #print descript

    dWords = {}
    for word in descript.split():
        word = sStem(word)
        word = word.strip().lower()
        if word == '': continue
        if word in lsAllWords: 
            indexWord = lsAllWords.index(word)
        else:
            lsAllWords.append(word)
            indexWord = len(lsAllWords)-1
    
        if indexWord in dWords.keys():
            dWords[indexWord]+=1
        else:
            dWords[indexWord]=1

    indices = dWords.keys()
    indices.sort()
    for index in indices:
        fTrain.write('%d:%d ' % (index,dWords[index]))
    fTrain.write('\n')
    return fTrain,lsAllWords



def build_file(lsFileNames,trainFile,wordFile,topicNum,lsSubtopics):
    
    f=None
    try:
        f = open(wordFile)
        lsAllWords = simplejson.load(f)
    except Exception,ex:
        print ex
        lsAllWords = []
    
    lsClassif = []
    fTrain = open(trainFile ,'w')
    lsAllWords = []
    index=0
    for fileName in lsFileNames:
        fDictReader = csv.DictReader(open(fileName,'rU'))
        print fileName
        for row in fDictReader:
            #print index
            index+=1
            try:
                classif = int(row['Subtopic'])
            except Exception:
                #problem w/ decimal...
                pass
                
            #don't use row if not in subtopics...
            if int(row['Major']) == topicNum and classif not in lsSubtopics:
                continue
            elif classif not in lsSubtopics:
                classif=0 
            if classif not in lsClassif:
                lsClassif.append(classif)
            
            descript = row['Title']
            fTrain,lsAllWords = writeFileBigram(descript,lsAllWords,fTrain,classif)
    
    fTrain.close()
    if f: 
        f.close()
    
    simplejson.dump(lsAllWords,open(wordFile,'w'))
    lsClassif.sort()
    print lsClassif
    
def predict(testFile,modelFile,outFile):
    command = 'svm-predict %s %s %s' % (testFile,modelFile,outFile)

    lsOut = os.popen(command).readlines()
    #print lsOut
    try:
        if lsOut[0].find('100') > -1:
            return True
        return False
    except Exception:
        print testFile
        
def test(sentence,modelFile,wordsFile,rangeFile,modelDir,subTopicCodes):
    #print sentence
    #print "******************************"
    testFile = '%s/test.txt' % modelDir
    scaleTestFile = '%s/scale_test.txt' % modelDir
    outFile = '%s/out.txt' % modelDir
    
    lsAllWords = simplejson.load(open(wordsFile))
    
    for scode in subTopicCodes:
        fTest = open(testFile,'w')
        fTest,lsAllWords = writeFile(sentence,lsAllWords,fTest,scode)
        fTest.close()
        scale_file(testFile,scaleTestFile,rangeFile,False)
        #print scode
        #print '------------------------'
        correct = predict(scaleTestFile,modelFile,outFile)
        if correct:
            return scode
    return -1

def classify(text,lsTopics=None):
    lsCodes = []
    for topic in dJT.values():
        if (lsTopics and topic in lsTopics) or not lsTopics:
            #print 'HERE IN CLASSIFY'
            #print 'TOPIC CODE IS %d' % topic.code
            tempDir = modelDir + dDir[topic.code]
            #print 'TEMP DIR IS %s' % tempDir
            modelFile=  tempDir + '/m.model'
            wordsFile = tempDir + '/words.txt'
            rangeFile = tempDir + '/range_train.txt'
            subTopicCodes = [st.code for st in JonesSubTopic.objects.filter(topic=topic)]
            sCode = test(text,modelFile,wordsFile,rangeFile,tempDir,subTopicCodes)
            if sCode != 0 and sCode!=-1:
                lsCodes.append(JonesSubTopic.objects.filter(code=sCode)[0])
    return lsCodes

def trainAll():
    lsFiles = ['/Users/lisagandy/Desktop/bills_topics_merge/108/108_bills.csv','/Users/lisagandy/Desktop/bills_topics_merge/109/109_bills.csv']

    for code,dir in dDir.items():
        print code
        modelDir = '/Users/lisagandy/Desktop/classif_bigram/%s' % dir
        os.popen('mkdir %s' % modelDir)
        subtopicCodes = [subtopic.code for subtopic in JonesSubTopic.objects.filter(topic__code=code)]
        subtopicCodes = [code for code in subtopicCodes if JonesSubTopic.objects.filter(code=code)[0].name.find('eneral') == -1 and JonesSubTopic.objects.filter(code=code)[0].name.lower().find('other') == -1]
        print subtopicCodes
        train(lsFiles,code,subtopicCodes,modelDir)

    
if __name__ == '__main__':
    trainAll()
    assert 0
    
    print classify('9/9/2009--Passed Senate amended. Travel Promotion Act of 2009 - Establishes the Corporation for Travel Promotion as an independent nonprofit corporation. Makes the Corporation subject to the provisions of the District of Columbia Nonprofit Corporation Act. Expresses the sense of Congress that the Corporation should not engage in lobbying activities. Requires the Corporation, among other things, to provide useful information to people interested in traveling to the United States, counter and correct misperceptions regarding U.S. entry policy, and promote U.S. travel. Requires the Corporation to develop and maintain a publicly accessible website. Requires the Corporation to establish annual objectives and an annual marketing plan and to submit an annual Corporation activities report to Congress. Establishes in the Treasury the Travel Promotion Fund and requires non-federal matching funds. Amends the Immigration and Nationality Act to require (under current law, authorize) the Secretary of Homeland Security to establish and collect a fee for the use of an electronic data sharing system concerning the admissibility of certain aliens into the United States that will ensure recovery of the full costs of providing and administering such system. Terminates such fee following FY2014. Authorizes the Corporation to impose an annual assessment on U.S. members of the travel and tourism industry represented on the Board of Directors of the Corporation. Amends the International Travel Act of 1961 to establish in the Department of Commerce the Office of Travel Promotion, to be headed by a Director. Requires that the Office of Travel and Tourism Industries expand its research and development activities to promote international travel to the United States. Authorizes appropriations.')
    assert 0


    
    
    print classify('To prevent duplication in the Federal government. SA 1611. Mr. HATCH submitted an amendment intended to be proposed to amendment SA 1511 proposed by to the bill S. 1390, to authorize appropriations for fiscal year 2010 for military activities of the Department of Defense, for military construction, and for defense activities of the Department of Energy, to prescribe military personnel strengths for such fiscal year, and for other purposes;')
    #assert 0
    
    print classify('to authorize appropriations for fiscal year 2010 for military activities of the Department of Defense, for military construction, and for defense activities of the Department of Energy, to prescribe military personnel strengths for such fiscal year, and for other purposes; as follows:')
    assert 0
    
    lsFiles = ['/Users/lisagandy/Desktop/bills_topics_merge/108/108_bills.csv','/Users/lisagandy/Desktop/bills_topics_merge/109/109_bills.csv']
    modelDir = '/Users/lisagandy/Desktop/classif/pub'
    modelFile,wordFile,rangeFile = train(lsFiles,topicCodePub,subTopicCodesPub,modelDir)
    
    rangeFile = '%s/range_train.txt' % modelDir
    wordFile = '%s/words.txt' % modelDir
    modelFile = '%s/m.model' % modelDir
    
    dictReader = csv.DictReader(open('/Users/lisagandy/Desktop/test_workbook.csv','rU'))
    for row in dictReader:
        sentence = row['descript']
        print sentence
        print "****************************"
        print test(sentence,modelFile,wordFile,rangeFile,modelDir,subTopicCodesPub)
        print ""
        
        
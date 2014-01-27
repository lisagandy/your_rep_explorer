import simplejson
import stemming.lovins 
import stemming.porter
from pyUtilities import *
import os
from paths import *

global_path = '/Users/lisagandy/Desktop/www2012/bills_topics_merge/'
global_path_subtopics = '%s/subtopics/' % global_path
weka_path = '/Users/lisagandy/Desktop/weka-3-6-1/weka.jar'

stopWords = []
text = open(CCU_DATA_PATH + '/weka_stopwords.txt').read()
for line in text.split('\n')[2:-1]:
    stopWords.append(line.split('.')[1])
  
dPred={}
dPred[0] = 1
dPred[1] = 2
dPred[2] = 3
dPred[3] = 4
dPred[4] = 5
dPred[5] = 6
dPred[6] = 7
dPred[7] = 8
dPred[8] = 10
dPred[9] = 12
dPred[10] = 13
dPred[11] = 14
dPred[12] = 15
dPred[13] = 16
dPred[14] = 17
dPred[15] = 18
dPred[16] = 19
dPred[17] = 20
dPred[18] = 21
dPred[19] = 99
dPred[20] = 26
dPred[21] = 27

dAttrs={}
dAttrs[1] = '@attribute Subtopic {100.0,104.0,105.0,107.0,108.0,101.0,103.0,121.0}'
dAttrs[2] = '@attribute Subtopic {200.0,201.0,202.0,204.0,205.0,206.0,207.0,208.0,299.0,209.0}'
dAttrs[3] = '@attribute Subtopic {300.0,301.0,302.0,321.0,322.0,323.0,324.0,325.0,331.0,332.0,333.0,334.0,335.0,336.0,341.0,343.0,344.0,398.0,399.0,326.0,342.0,389.0}'
dAttrs[4] = '@attribute Subtopic {400.0,401.0,402.0,403.0,404.0,405.0,498.0,499.0}'
dAttrs[5] = '@attribute Subtopic {500.0,501.0,502.0,503.0,504.0,505.0,506.0,508.0,529.0,530.0,599.0}'
dAttrs[6] = '@attribute Subtopic {600.0,601.0,602.0,603.0,606.0,607.0,609.0,698.0,699.0,604.0}'
dAttrs[7] = '@attribute Subtopic {700.0,701.0,703.0,704.0,705.0,707.0,708.0,709.0,710.0,711.0,798.0,799.0}'
dAttrs[8] = '@attribute Subtopic {800.0,801.0,802.0,803.0,805.0,806.0,807.0,898.0,899.0,860.0}'
dAttrs[10] = '@attribute Subtopic {1000.0,1001.0,1002.0,1003.0,1005.0,1006.0,1007.0,1010.0,1098.0,1099.0}'
dAttrs[12] = '@attribute Subtopic {1200.0,1201.0,1202.0,1203.0,1204.0,1205.0,1206.0,1207.0,1208.0,1209.0,1210.0,1211.0,1299.0}'
dAttrs[13] = '@attribute Subtopic {1300.0,1301.0,1302.0,1303.0,1304.0,1305.0,1399.0}'
dAttrs[14] = '@attribute Subtopic {1400.0,1401.0,1403.0,1405.0,1406.0,1407.0,1408.0,1409.0,1410.0,1499.0,1404.0}'
dAttrs[15] = '@attribute Subtopic {1500.0,1501.0,1502.0,1504.0,1505.0,1507.0,1520.0,1521.0,1522.0,1523.0,1524.0,1525.0,1526.0,1599.0}'
dAttrs[16] = '@attribute Subtopic {1600.0,1602.0,1603.0,1604.0,1605.0,1606.0,1608.0,1609.0,1610.0,1611.0,1612.0,1614.0,1615.0,1616.0,1617.0,1620.0,1698.0,1699.0,1619.0,1618.0}'
dAttrs[17] = '@attribute Subtopic {1700.0,1701.0,1704.0,1706.0,1707.0,1708.0,1709.0,1798.0,1799.0,1705.0}'
dAttrs[18] = '@attribute Subtopic {186.0,1800.0,1802.0,1803.0,1804.0,1806.0,1807.0,1808.0,1801.0,1899.0}'
dAttrs[19] = '@attribute Subtopic {1900.0,1901.0,1902.0,1905.0,1906.0,1907.0,1908.0,1909.0,1910.0,1912.0,1914.0,1919.0,1920.0,1925.0,1926.0,1927.0,1929.0,1999.0,1911.0}'
dAttrs[20] = '@attribute Subtopic {2000.0,2001.0,2002.0,2003.0,2004.0,2005.0,2006.0,2007.0,2008.0,2009.0,2011.0,2012.0,2013.0,2014.0,2015.0,2030.0,2099.0}'
dAttrs[21] = '@attribute Subtopic {2100.0,2101.0,2102.0,2103.0,2104.0,2105.0,2199.0}'
dAttrs[26] = '@attribute Subtopic {2600.0}'
dAttrs[27] = '@attribute Subtopic {2700.0}'
dAttrs[99] = '@attribute Subtopic {9999.0,9900.0}'



def temp_util():
    lsAll=[]
    f = open('/Users/lisagandy/Desktop/www2012/bills_topics_merge/train_out3.arff')
    
    lines = f.readlines()
    for line in lines:
        if line.find('@attribute') > -1:
            lsAll.append(line.split()[1])
    
    f.close()
    fOut = open('/Users/lisagandy/Desktop/www2012/bills_topics_merge/stemmed_words_training.arff','w')
    fOut.write(simplejson.dumps(lsAll[0:-1]))
    fOut.close()
    
def temp_util_subtopics():    
    
    global dPred
    
    for val in dPred.values():
        
        lsAll=[]
        f = open('/Users/lisagandy/Desktop/www2012/bills_topics_merge/subtopics/train_out_%d_3.arff' % val)
    
        lines = f.readlines()
        for line in lines:
            if line.find('@attribute') > -1:
                lsAll.append(line.split()[1])
    
        f.close()
        fOut = open('/Users/lisagandy/Desktop/www2012/bills_topics_merge/subtopics/stemmed_words_%d_training.arff' % val,'w')
        fOut.write(simplejson.dumps(lsAll[0:-1]))
        fOut.close()


@benchmark
def create_fake_arff(text,predict):
    global stopWords
    global global_path
    global weka_path
    
    fOut = open('%stest_fake.arff' % global_path,'w')
    textToWrite = "@relation 'master_topic-weka.filters.unsupervised.attribute.StringToWordVector-R1-W20000-prune-rate-1.0-C-N0-L-S-stemmerweka.core.stemmers.LovinsStemmer-M2-O-tokenizerweka.core.tokenizers.WordTokenizer -delimiters \" \\r\\n\\t.,;:\\\'\\\"()?!\"-weka.filters.unsupervised.attribute.Reorder-R2-last,first'\n\n"
    
    lsAll = simplejson.load(open('%sstemmed_words_training.arff' % global_path))
    for word in lsAll:
        textToWrite += '@attribute %s numeric\n' %  word
    
    textToWrite+='@attribute Major {1.0,2.0,3.0,4.0,5.0,6.0,7.0,8.0,10.0,12.0,13.0,14.0,15.0,16.0,17.0,18.0,19.0,20.0,21.0,99.0,26.0,27.0}\n\n'
    textToWrite+='@data\n\n'
    
    text = ' '.join([w for w in text.split() if not w in stopWords])
    
    fOut2 = open('%stemp_out.txt' % global_path,'w')
    fOut2.write(text)
    fOut2.close()
   
    
    runjava = 'java -classpath %s' % weka_path
    command = '%s weka.core.stemmers.LovinsStemmer -i %stemp_out.txt' % (runjava,global_path)
    stemmedText = os.popen(command).read()
    dWords = {}
    for word in stemmedText.split():
        try:
            index = lsAll.index(word)
            if index in dWords:
                dWords[index]+=1
            else:
                dWords[index] = 1
        
        except Exception:
            pass

    words = dWords.keys()
    words.sort()
    numWords = []
    for word in words:
        numWords.append(dWords[word])
        
    #print words
    #print numWords
    textOut = '{'
    for word,numWord in zip(words,numWords):
        textOut = textOut + '%s %s,' % (word,numWord)
    
    textOut = textOut + '5515 %d.0}\n\n' % predict
    textToWrite += textOut
    #print textToWrite
    
    fOut.write(textToWrite)
    fOut.close()
    return '%stest_fake.arff' % global_path

def create_fake_arff_subtopics(text,subtopic_num,predict):
        global stopWords
        global global_path_subtopics
        global weka_path
        
        fOut = open('%stest_fake_%d.arff' % (global_path_subtopics,subtopic_num),'w')
        textToWrite = "@relation 'subtopic_%d_topic-weka.filters.unsupervised.attribute.StringToWordVector-R1-W20000-prune-rate-1.0-C-N0-L-S-stemmerweka.core.stemmers.LovinsStemmer-M2-O-tokenizerweka.core.tokenizers.WordTokenizer -delimiters \" \\r\\n\\t.,;:\\\'\\\"()?!\"-weka.filters.unsupervised.attribute.Reorder-R2-last,first'\n\n" % subtopic_num

        lsAll = simplejson.load(open('%sstemmed_words_%d_training.arff' % (global_path_subtopics,subtopic_num)))
        for word in lsAll:
            textToWrite += '@attribute %s numeric\n' %  word

        textToWrite+='%s\n\n' % dAttrs[subtopic_num]
        textToWrite+='@data\n\n'

        text = ' '.join([w for w in text.split() if not w in stopWords])

        fOut2 = open('%stemp_out.txt' % global_path_subtopics,'w')
        fOut2.write(text)
        fOut2.close()

        
        runjava = 'java -classpath %s' % weka_path
        command = '%s weka.core.stemmers.LovinsStemmer -i %stemp_out.txt' % (runjava,global_path_subtopics)
        stemmedText = os.popen(command).read()
        dWords = {}
        for word in stemmedText.split():
            try:
                index = lsAll.index(word)
                if index in dWords:
                    dWords[index]+=1
                else:
                    dWords[index] = 1

            except Exception:
                pass

        words = dWords.keys()
        words.sort()
        numWords = []
        for word in words:
            numWords.append(dWords[word])

        #print words
        #print numWords
        textOut = '{'
        for word,numWord in zip(words,numWords):
            textOut = textOut + '%s %s,' % (word,numWord)
            
        textOut = textOut + '%d %d.0}\n\n' % (len(lsAll),predict)
        textToWrite += textOut
        #print textToWrite

        fOut.write(textToWrite)
        fOut.close()
        return '%stest_fake_%d.arff' % (global_path_subtopics,subtopic_num)
 
if __name__ == '__main__':
    assert 0
    pass
    #temp_util()
    #create_fake_arff_subtopics('to repeal section 801 of the revenue act of 1916',1,108)
    #create_fake_arff_subtopics('to require any amounts appropriated for members representational allowances for the house of representatives for a fiscal year that remain after all payments are made from such allowances for the year to be deposited in the treasury and used f',1,100)
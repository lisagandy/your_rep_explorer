import csv
import os
from pyUtilities import *
from create_fake_arff import create_fake_arff, create_fake_arff_subtopics
from download_votes import genericAmendText
from ccu_gen_beta.models import *
from django.utils.encoding import smart_str

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

dCh = {}
dCh[1] = [100,104,105,107,108,101,103,121]
dCh[2] = [200,201,204,205,206,207,208,299,209]
dCh[3] = [300,301,302,321,322,323,324,325,331,332,333,334,335,336,341,343,344,398,399,326,343,389]
dCh[4] = [400,401,402,403,404,405,498,499]
dCh[5] = [500,501,502,503,504,505,506,508,529,530,599]
dCh[6] = [600,601,602,603,606,607,609,698,699,604]
dCh[7] = [700,701,703,704,705,707,708,709,710,711,798,799]
dCh[8] = [800,801,802,803,805,806,807,898,899,860]
dCh[10] = [1000,1001,1002,1003,105,1006,1007,1010,1098,1099]
dCh[12]=[1200,1201,1202,1203,1204,1205,1206,1207,1208,1209,1210,1211,1299]
dCh[13] = [1300,1301,1302,1303,1304,1305,1399]
dCh[14] = [1400,1401,1403,1405,1406,1407,1408,1409,1410,1499,1404]
dCh[15]=[1500,1501,1502,1504,1505,1507,1520,1521,1522,1523,1524,1525,1526,1599]
dCh[16]=[1600,1602,1603,16041605,1606,168,1609,1610,1611,1612,1614,1615,1616,1617,1620,1698,1699,1619,1618]
dCh[17] = [1700,1701,1704,1706,1707,1708,1709,1798,1799,1705]
dCh[18]=[186,1800,1802,1803,1804,1806,1807,1808,1801,1899]
dCh[19]=[1900,1901,1902,1905,1906,1907,1908,1909,1910,1912,1914,1919,1920,1925,1926,1927,1929,1999,1911]
dCh[20]=[2000,2001,2002,2003,2004,2005,2006,2007,2008,2009,2011,2012,2013,2014,2015,2030,2099]
dCh[21]=[2100,2101,2102,2103,2104,2105,2199]
dCh[26] = [2600]
dCh[27] = [2700]
dCh[99]=[9999,9900]

weka_path = '/Users/lisagandy/Desktop/weka-3-6-1/weka.jar'

def getPredSubtopic(topic_num):
    global dCh

    text = open('/Users/lisagandy/Desktop/out.txt').read()

    text = text.lower()
    text = text[text.find('confusion matrix')+len('confusion matrix'):]
    text = text[text.find('confusion matrix')+len('confusion matrix'):]
   
    text = text.split('\n')
    text = text[3:]
    for row in text:
        for index,col in enumerate(row.split()):
            if col=='1':
                return dCh[topic_num][index]

def create_subtopic_csvs():
    global dPred
    path = "/Users/lisagandy/Desktop/www2012/bills_topics_merge/"
    fileName = "%smaster.csv" % path
    
    for val in dPred.values():
        fIn = open(fileName,'rU')
        fDictReader = csv.DictReader(fIn)
        fileName2 = "%ssubtopics/subtopic_%d.csv" % (path,val)
        print fileName2
        fOut = open(fileName2,'w')
        fDictWriter = csv.DictWriter(fOut,['Title','Subtopic'])
        
        fOut.write('Title,Subtopic\n')
        for row in fDictReader:
            if int(row['Major']) == val:
                dOut = {}
                dOut['Title'] = row['Title']
                dOut['Subtopic'] = row['Subtopic']
                fDictWriter.writerow(dOut)
        
        
        fOut.close()
        fIn.close()

#create_subtopic_csvs()
#assert 0


def clean_up_text(text):
    text = removePunctuation(text)
    text = stripExtraSpaces(removePunctuation(text.lower()))
    return text
    
def clean_training_files():
    #Removes duplicates and cleans text to create a master csv file
    #----------------------------------------------------------------------
    path = "/Users/lisagandy/Desktop/www2012/bills_topics_merge/"
    filenames = ['%s107/107_words_only.csv' % path,'%s108/108_words_only.csv'% path,'%s109/109_words_only.csv'% path]
    fOut = open('%smaster_topic.csv' % path,'w')
    fDictWriter = csv.DictWriter(fOut,['Title','Major'])
    lsText = []
    lsMajor = []
    lsSub = []
    fOut.write('Title,Major\n')
    i = 0
    for filename in filenames:
         f = open(filename,'rU')
         for row in csv.DictReader(f):
             descript = row['Title']
             text = clean_up_text(descript)
             if text in lsText:
                 continue
             
             i+=1
             if i%100 == 0:
                 print i
                 
             lsText.append(text)
             lsMajor.append(row['Major'])
             #lsSub.append(row['Subtopic'])
             
             dOut = {}
             dOut['Title'] = text
             dOut['Major'] = row['Major']
             #dOut['Subtopic'] = row['Subtopic']
             fDictWriter.writerow(dOut)
    
    fOut.close()

def create_training_file():
    path = '/Users/lisagandy/Desktop/www2012/bills_topics_merge/'  
    global weka_path
    runjava = 'java -classpath %s' % weka_path
    
    command1 = '%s weka.core.converters.CSVLoader -S 1 -N 2 %smaster_topic.csv > %strain_out1.arff' % (runjava,path,path)
    os.popen(command1)
    
    command1 = '%s weka.filters.unsupervised.attribute.StringToWordVector -L -S -M 2 -O -C -W 20000 -stemmer weka.core.stemmers.LovinsStemmer -i %strain_out1.arff -o %strain_out2.arff' % (runjava,path,path)
    os.popen(command1)

    command1 = '%s weka.filters.unsupervised.attribute.Reorder -R 2-last,first -i %s/train_out2.arff > %s/train_out3.arff' % (runjava,path,path)
    os.popen(command1)
  
def create_training_file_subtopic():
    global dPred
    
    for subtopic_num in dPred.values():
        path = '/Users/lisagandy/Desktop/www2012/bills_topics_merge/subtopics/'  
        global weka_path
        runjava = 'java -classpath %s' % weka_path

        command1 = '%s weka.core.converters.CSVLoader -S 1 -N 2 %ssubtopic_%d.csv > %strain_out_%d_1.arff' % (runjava,path,subtopic_num,path,subtopic_num)
        os.popen(command1)

        command1 = '%s weka.filters.unsupervised.attribute.StringToWordVector -L -S -M 2 -O -C -W 20000 -stemmer weka.core.stemmers.LovinsStemmer -i %strain_out_%d_1.arff -o %strain_out_%d_2.arff' % (runjava,path,subtopic_num,path,subtopic_num)
        os.popen(command1)

        command1 = '%s weka.filters.unsupervised.attribute.Reorder -R 2-last,first -i %s/train_out_%d_2.arff > %s/train_out_%d_3.arff' % (runjava,path,subtopic_num,path,subtopic_num)
        os.popen(command1)  

# create_training_file_subtopic()
# assert 0  

def getPredTopic():
    global dPred

    text = open('/Users/lisagandy/Desktop/out.txt').read()

    text = text.lower()
    text = text[text.find('confusion matrix')+len('confusion matrix'):]
    text = text[text.find('confusion matrix')+len('confusion matrix'):]
   
    text = text.split('\n')
    text = text[3:]
    for row in text:
        for index,col in enumerate(row.split()):
            if col=='1':
                return dPred[index]


def predCorrect(fileName):
    fOpen = open(fileName)
    text = fOpen.read()
    text = text.lower()
    text = text[text.find('correctly classified instances')+500:]
    text = text[text.find('correctly classified instances')+len('correctly classified instances'):]
    text = text[:text.find('\n')]
    if text.find('100') > -1:
        return True
    else:
        return False
    
#@benchmark 
def cross_validate(trainFile,testFile):
    global weka_path
    runjava = 'java -classpath %s' % weka_path
    
    #modelFile = '/Users/lisagandy/Desktop/www2012/bills_topics_merge/model.m'
    
    outFile = '/Users/lisagandy/Desktop/out.txt'
    
    command = '%s weka.classifiers.bayes.ComplementNaiveBayes -t %s -T %s > %s' % (runjava,trainFile,testFile,outFile)
    os.popen(command)
   

def validate_system():
    fOut = open('/Users/lisagandy/Desktop/www2012/bills_topics_merge/master_topic.csv')
    fDictReader = csv.DictReader(fOut)
    correct = 0
    num_rows = 0
    for row in fDictReader:
        if int(row['Major']) != 15:
            continue
        
        testText = row['Title'] 
        
        testFile = create_fake_arff(testText,int(row['Major']))
        cross_validate('%strain_out3.arff' % '/Users/lisagandy/Desktop/www2012/bills_topics_merge/',testFile)
        
        if predCorrect('/Users/lisagandy/Desktop/out.txt'):
            correct+=1
        
        
        num_rows+=1
        print getPredTopic()
        print num_rows
        print correct
        print float(correct)/num_rows
        print ""
        

def validate_system_subtopics():
    fOut = open('/Users/lisagandy/Desktop/www2012/bills_topics_merge/master.csv')
    fDictReader = csv.DictReader(fOut)
    correct = 0
    num_rows = 0
    for row in fDictReader:
        if int(row['Major']) != 1:
            continue
            
        testText = row['Title'] 

        testFile = create_fake_arff_subtopics(testText,int(row['Major']),int(row['Subtopic']))
        cross_validate('%strain_out_1_3.arff' % '/Users/lisagandy/Desktop/www2012/bills_topics_merge/subtopics/',testFile)

        if predCorrect('/Users/lisagandy/Desktop/out.txt'):
            correct+=1

        num_rows+=1
        #print getPredTopic()
        print num_rows
        print correct
        print float(correct)/num_rows
        print ""
        assert 0

def findJonesSubTopicVotes(session):
        global dCh
    
        #for vote in Vote.objects.filter(number=233,bill__prefix='h',bill__number=3672):
        for i,vote in enumerate(Vote.objects.filter(Q(bill__congress__number=session)|Q(amendment__bill__congress__number=session))):
            print i
            if (vote.bill.subtopicsAssigned or (vote.amendment and vote.amendment.subtopicsAssigned)) and vote.senateVote==True:
                print 'SUBTOPIC ALREADY ASSIGNED'
                continue
                
            try:
                start = datetime.datetime.now()
                print ""
                print vote
                if vote.amendment and vote.amendment.subtopics.all().count()==0:
                    #return
                    #use text of amendment to find subtopics....
                    amendmentText = None
                    if not genericAmendText(vote.amendment.purpose):
                        amendmentText = vote.amendment.purpose
                        testFile = create_fake_arff(amendmentText,1)
                        print 'AMENDMENT TEXT'
                        print amendmentText
                        cross_validate('%strain_out3.arff' % '/Users/lisagandy/Desktop/www2012/bills_topics_merge/',testFile)
                        topicNum = getPredTopic()
                        print JonesTopic.objects.filter(code=topicNum)
                    
                        testFile = create_fake_arff_subtopics(amendmentText,topicNum,dCh[topicNum][0])
                        cross_validate('%strain_out_%d_3.arff' % ('/Users/lisagandy/Desktop/www2012/bills_topics_merge/subtopics/',topicNum),testFile)
                        subtopicNum = getPredSubtopic(topicNum)
                        print JonesSubTopic.objects.filter(code=subtopicNum)
                        vote.amendment.subtopics = JonesSubTopic.objects.filter(code=subtopicNum)
                        vote.amendment.subtopicsAssigned=True
                        vote.amendment.save()
                        end = datetime.datetime.now()
                        delta = end-start
                        print delta.seconds
                        print delta.microseconds
                        assert 0
                    
                    else:
                        print 'generic amendment'
                        print vote.amendment.purpose

                elif vote.bill.summary.strip() != "" and vote.bill.subtopics.all().count()==0: 
                      summary = smart_str(vote.bill.summary)
                      if len(summary) > 5000:
                          summary = summary[0:5000]
                      
                      testFile = create_fake_arff(summary,1)
                      try:
                          print vote.bill.otherTitles.all()[0].title
                      except Exception,ex:
                          print ex
                          pass
                      cross_validate('%strain_out3.arff' % '/Users/lisagandy/Desktop/www2012/bills_topics_merge/',testFile)
                      topicNum = getPredTopic()
                      print JonesTopic.objects.filter(code=topicNum)
                      testFile = create_fake_arff_subtopics(summary,topicNum,dCh[topicNum][0])
                      cross_validate('%strain_out_%d_3.arff' % ('/Users/lisagandy/Desktop/www2012/bills_topics_merge/subtopics/',topicNum),testFile)
                      subtopicNum = getPredSubtopic(topicNum)
                      print JonesSubTopic.objects.filter(code=subtopicNum)
                      vote.bill.subtopics = JonesSubTopic.objects.filter(code=subtopicNum)
                      vote.bill.subtopicsAssigned=True
                      vote.bill.save()
                      end = datetime.datetime.now()
                      delta = end-start
                      print delta.seconds
                      print delta.microseconds
                      assert 0
                else:
                    print "NOT VALID AMENDMENT OR BILL TEXT"
            
            
            except Exception,ex:
                print ex
                print "SOME KIND OF EXCEPTION"      
        
if __name__ == '__main__':
    #Bill.objects.all().update(subtopicsAssigned=False)
    #Amendment.objects.all().update(subtopicsAssigned=False)
    #findJonesSubTopicVotes(111)
    findJonesSubTopicVotes(112)
    #validate_system()
    #validate_system_subtopics()
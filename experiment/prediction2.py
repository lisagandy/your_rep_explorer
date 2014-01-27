import pyUtilities as pyU
import csv
from svmutil import *
import simplejson
from pyStemmer import *

def build_training_file(out_file,words_file):
    fOut = open(out_file,'w')
    lsAllWords = []
    for i in range(108,110):
        fDictReader = csv.DictReader(open('/Users/lisagandy/Desktop/bills_topics_merge/%d/%d_bills.csv' % (i,i),'rU'))
        for row in fDictReader:

            classif = row['Major']
            if classif=='3':
                classif='3'
                #classif=row['Subtopic']
            else:
                classif='0'
        
            #if classif!= '15':
                #classif='0'
            
            descript = row['Title']
            descript = pyU.removePunctuation(descript)
            descript = pyU.sStripStopWordsAll(descript)
            fOut.write(classif+' ')
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
        
            #print dWords
            #assert 0
            indices = dWords.keys()
            indices.sort()
            for index in indices:
                fOut.write('%d:%d ' % (index,dWords[index]))
            fOut.write('\n')
            
    #print lsAllWords
    f = open(words_file,'w')
    simplejson.dump(lsAllWords,f)
    
    

def train(train_file,outfile):            
    classes,data = svm_read_problem(train_file)
    #print classes
    #print data
    #assert 0
    prob = svm_problem(classes,data)
    #param = svm_parameter('-t 2')
    m = svm_train(prob)
    svm_save_model(outfile,m)
    #param = svm_parameter('-t 2 -v 5')
    #svm_train(prob,param)
   

def classify(model_file,test_file,words_file):
    #m = svm_load_model(model_file)
    #dWords = {0: 2, 1: 1, 2: 1, 3: 1, 4: 1, 5: 1, 6: 1, 7: 1, 8: 1, 9: 1, 10: 1, 11: 2, 12: 2, 13: 1, 14: 1, 15: 1}
    #x = []
    #x.append(dWords)
    #x = [{0:2, 1:1, 2:1, 3:1, 4:1, 5:1, 6:1, 7:1, 8:1, 9:1, 10:1, 11:2, 12:2, 13:1, 14:1, 15:1 }]
    #x = [{0:0.333333,1:0.5,2:0.333333 ,3:1, 4:0.333333, 5:0.25, 6:0.333333, 7:0.5, 8:0.333333, 9:0.25,10:0.333333, 11:0.666667, 12:0.5, 13:0.5, 14:0.333333, 15:0.5 }]
    #print  svm_predict([0],x,m)
    
    #assert 0
    fOut = open('/Users/lisagandy/Desktop/test_out.txt','w')
    words = simplejson.load(open(words_file))
    #print words[2930]
    #assert 0
    #m = svm_load_model(model_file)
    for row in csv.DictReader(open(test_file,'rU')):
        #print row['Title']
        lsTraining=[]
        descript = row['descript']
        descript = pyU.removePunctuation(descript)
        descript = pyU.sStripStopWordsAll(descript)
        #print descript
        dWords={}
        lsWords = descript.split()
        for word in lsWords:
            
            word = sStem(word)
            word = word.strip().lower()
            #print word
            if word in words:
                indexWord = words.index(word)
                if indexWord in dWords.keys():
                    dWords[indexWord]+=1
                else:
                    dWords[indexWord]=1
        
        #print dWords
        #assert 0
        fOut.write('0 ')
        indices = dWords.keys()
        indices.sort()
        for index in indices:
            fOut.write('%d:%d ' % (index,dWords[index]))
        fOut.write('\n')
    fOut.close()    
        
        #x0,max_idx = gen_svm_nodearray(dWords)
        #print x0
        #print libsvm.svm_predict(m,x0)
        #print dWords

    
    
if __name__ == '__main__':
    build_training_file('/Users/lisagandy/Desktop/classif/train_108_109_health.txt','/Users/lisagandy/Desktop/classif/108_109_words.txt')
    assert 0
    #train('/Users/lisagandy/Desktop/train_107_health.txt','/Users/lisagandy/Desktop/train_107_health.model')
    #assert 0
    #classify('/Users/lisagandy/Desktop/scale.model','/Users/lisagandy/Desktop/test_workbook.csv','/Users/lisagandy/Desktop/108_words.txt')
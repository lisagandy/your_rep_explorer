from ccu_gen_beta.models import *
from pyUtilities import *
import os
import csv

def clean_up_text(text):
    text = removePunctuation(text)
    text = stripExtraSpaces(removePunctuation(text.lower()))
    return text

path = "/Users/lisagandy/Desktop/icwsm2012/"
filenames = ['%s%s' % (path,'master.csv')]
newpath = "/Users/lisagandy/Desktop/icwsm2012/class_files"

allNums = []

for filename in filenames:
    print filename
    f = open(filename,'rU')
    for row in csv.DictReader(f):
        descript = row['Title']
        text = clean_up_text(descript)
        topicNum = row['Major']

        try: 
            os.popen('mkdir %s/%s' % (newpath,topicNum)) 
        except Exception:
            pass #already created
        
        fileNum = '%s_%d.txt' %(topicNum,random.randrange(1,1000000))
        
        if fileNum in allNums:
            fileNum = '%s_%d.txt' %(topicNum,random.randrange(1,1000000))
            print 'DUPLICATE FILE'
        else:
            allNums.append(fileNum)
            
        newFile = open("%s/%s/%s" % (newpath,topicNum,fileNum),'w')
        newFile.write(descript)
        newFile.close()

assert 0        
path = "/Users/lisagandy/Desktop/icwsm2012/"
filenames = ['%s%s' % (path,'master.csv')]

newpath = "/Users/lisagandy/Desktop/icwsm2012/class_files_subtopic"
allNums = []

for filename in filenames:
    print filename
    f = open(filename,'rU')
    for row in csv.DictReader(f):
        descript = row['Title']
        text = clean_up_text(descript)
        topicNum = row['Major']
        subtopicNum = row['Subtopic']

        #try to create topic dir
        try: 
            os.popen('mkdir %s/%s' % (newpath,topicNum)) 
        except Exception:
            pass #already created
        
        #try to create subtopic dir
        try: 
            os.popen('mkdir %s/%s/%s' % (newpath,topicNum,subtopicNum)) 
        except Exception:
            pass #already created
        
        fileNum = '%s_%s_%d.txt' %(topicNum,subtopicNum,random.randrange(1,1000000))
        
        if fileNum in allNums:
            fileNum = '%s_%s_%d.txt' %(topicNum,subtopicNum,random.randrange(1,1000000))
            print 'DUPLICATE FILE'
        else:
            allNums.append(fileNum)
            
        newFile = open("%s/%s/%s/%s" % (newpath,topicNum,subtopicNum,fileNum),'w')
        newFile.write(descript)
        newFile.close()        
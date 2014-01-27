import csv


path = "/Users/lisagandy/Desktop/www2012/bills_topics_merge/"
fileName = '%smaster.csv' % path
i = 0
fOut = open('/Users/lisagandy/master_reduced.csv','w')
fOut.write('Title,Major')
fOut.write('\n')
fDictWriter = csv.DictWriter(fOut,['Title','Major'])
dTrack={}

i=0

f = open(fileName,'rU')
    
for i,row in enumerate(csv.DictReader(f)):
    label = int(row['Major'])
    #print label
    if label in dTrack:
        if dTrack[label] > 50:
            continue
        else:
            del row['Subtopic']
            fDictWriter.writerow(row)
            dTrack[label]+=1
    else:
        del row['Subtopic']
        fDictWriter.writerow(row)
        dTrack[label]=1 

    print i
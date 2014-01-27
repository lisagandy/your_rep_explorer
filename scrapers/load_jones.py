import re
import pyUtilities as pyU
from ccu_gen_beta.models import *
from paths import *

def loadJones():
    txt = open(CCU_DATA_PATH + 'jones.txt').read()
    reSub = re.compile('(\d+\:)')
    reMainTop = re.compile('(\d+\.)')
    lsMain = re.split(reMainTop,txt)
    lsMain = [section.strip() for section in lsMain if section.strip()!=""]
   
    for index in range(0,len(lsMain),2):
        code = int(lsMain[index].replace('.',''))
        
        sectionName = pyU.toascii(lsMain[index+1].split('\n')[0]).strip()
        jt,notThere = JonesTopic.objects.get_or_create(name=sectionName)
        jt.code = code
        jt.save()
        section = pyU.toascii(' '.join(lsMain[index+1].split('\n')[1:]))
        subSecs = [sec for sec in re.split(reSub,section) if sec!=""] #and sec.lower().find('examples') > -1]
        print sectionName
        print code
        print "************************"
        
        subcode=None
        for sub in subSecs:
            #print sub
            m = re.search('(\d+):',sub)
            if m:
                subcode = int(m.group(0).replace(':',''))
                #print subcode
                continue
            
            subName = pyU.toascii(sub.split('Examples:')[0].strip())
            subName = pyU.toascii(subName.split('Major Topic Codes')[0].strip())
            print 'subname ' + subName
            if sub.find('xample') == -1:
                subsection = ""
            else:
                subsection = pyU.toascii(' '.join(sub.split('Examples:')[1:]).strip())
                subsection = pyU.toascii(subsection.split('See also:')[0].strip())
            
            print 'subcode ' + str(subcode)
            print 'subsection ' + subsection
            print ""
            try:
                jst,notThere = JonesSubTopic.objects.get_or_create(name=subName,descript=subsection,topic=jt)
                jst.code = subcode
                jst.save()
            except Exception,ex:
                print ex
                
        
if __name__ == '__main__':
    loadJones()
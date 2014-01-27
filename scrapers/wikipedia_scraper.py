from BeautifulSoup import BeautifulSoup
from pyUtilities import _getFile,toascii,stripWords,__getFile
import time
import urllib

def wikiScraperFirstTwoParas(term):
    
    found = False
    i = 0
    while not found:
        html = _getFile('http://en.wikipedia.org/wiki/%s' % term.replace(' ','_'))
        if i==2:
            return None
        if html.find('technical problem') > -1 or html.find('Other reasons') > -1:
            print 'technical problem in wiki'
            time.sleep(2.0)
            i+=1
        else:
            found=True
        
        
    doc = BeautifulSoup(html)
    paras = doc.findAll('p')
    text = ' '
    
    if len(paras) >= 2:        
        paras = paras[0:2]
    elif len(paras) == 1:
        paras = paras[0:1]
    else:
        return None
        
    for para in paras:
        for indivText in para.findAll(text=True):
            try:
                text = text + ' ' + toascii(indivText)
            except Exception:
                continue
                
    text = stripWords(text)
    
    return text
    

if __name__ == '__main__':
    print wikiScraperFirstTwoParas('congressional officers and employees')
    
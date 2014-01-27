import math

from pyStemmer import sStem
from pyUtilities import bIsStopWord,removePunctuation,stripExtraSpaces
import re

_documents = {}
_words = {}

def add_document(title, text):
    text = _clean_text(text)
    for word in text.split():
        _words[word] = True
    _documents[title] = text

def add_document_unique(title, text):
    text = _clean_text_unique(text)
    for word in text.split():
        _words[word] = True
    _documents[title] = text

def clear():
    global _documents, _words
    _documents, _words = {}, {}
        
def classify_document(target_text):
    ret = {}
    target_text = _clean_text(target_text)
    for title, text in _documents.items():
        calculated_similarity = _similarity(target_text, text)
        ret[title] = calculated_similarity
    return ret


def classify_document_unique(target_text):
    ret = {}
    target_text = _clean_text_unique(target_text)
    for title, text in _documents.items():
        calculated_similarity = _similarity(target_text, text)
        ret[title] = calculated_similarity
    return ret
    
def _clean_text(text):
    reNum = re.compile('\d+')
    text = ' '.join([w for w in text.split() if not bIsStopWord(w)])
    text = sStem(text)
    text = re.sub(reNum,' ',text)
    return stripExtraSpaces(removePunctuation(text.lower()))

def _clean_text_unique(text):
    reNum = re.compile('\d+')
    text = ' '.join([w for w in text.split() if not bIsStopWord(w)])
    text = sStem(text)
    text = re.sub(reNum,' ',text)
    text = stripExtraSpaces(removePunctuation(text.lower()))
    lsText = text.split()
    lsTextU = []
    for word in lsText:
        if not word in lsTextU:
            lsTextU.append(word)
    return ' '.join([word for word in lsTextU])

   
def _magnitude(model):
    ret = 0
    for count in model.values():
        ret += count * count
    ret = math.sqrt(ret)
    return ret
    
def _similarity(lhs, rhs):
    #print 'here'
    ret = 0.0
    #print lhs
    #print rhs
    lhs_words, rhs_words = lhs.split(), rhs.split()
    lhs_model, rhs_model = {}, {}
    for word in lhs_words:
        lhs_model[word] = 1 + lhs_model.get(word, 0)
    for word in rhs_words:
        rhs_model[word] = 1 + rhs_model.get(word, 0)

    for word in _words:
        if word in lhs_model.keys() and word in rhs_model.keys():
            #print word
            ret += lhs_model[word] * rhs_model[word]
    
    
    #print lhs_model.keys()
    #     print rhs_model.keys()
    if _magnitude(lhs_model) * _magnitude(rhs_model) > 0:
    	ret /= (_magnitude(lhs_model) * _magnitude(rhs_model))
    else:
	ret = 0

    return ret

def cos_similarity(lhs, rhs):
    #print "here"
    ret = 0.0
    #lhs = _clean_text(lhs)
    #rhs = _clean_text(rhs)
    lhs_words, rhs_words = lhs.split(), rhs.split()
    lhs_model, rhs_model = {}, {}
    for word in lhs_words:
        lhs_model[word] = 1 + lhs_model.get(word, 0)
    for word in rhs_words:
        rhs_model[word] = 1 + rhs_model.get(word, 0)
      
    #print lhs_model
    #print rhs_model 
    lsWords = lhs_model.keys()
    lsWords.extend(rhs_model.keys())
    _words = list(set(lsWords)) 
    for word in _words:
        if word in lhs_model.keys() and word in rhs_model.keys():
            ret += lhs_model[word] * rhs_model[word]

    ret /= (_magnitude(lhs_model) * _magnitude(rhs_model))
    return ret
    
        
if __name__ == '__main__':
    add_document('foo','This is comprehensive legislation to overhaul regulations in the financial sector. It would establish a new Consumer Financial Protection Agency to regulate products like home mortgages, car loans and credit cards, give the Treasury Department new authority to place non-bank financial firms, like insurance companies into receivership, regulate the over-the-counter derivatives market, and more.')
    print classify_document('senate committee on finance')
    #add_document('foo', 'mortgage financing reform, consumer credit protection, real estate settlement procedures, consumer access to credit records, consumer information on credit card interest rates, consumer information on mortgage settlement costs, fraud and abuse among credit repair agencies, adjustable rate mortgages, regulation of credit card solicitations, inaccurate credit bureau information reporting procedures, Credit Control Act. See also: 1410 government mortgage programs.')
    #add_document('foo','Provider and insurer and regulation reimbursement rates and methods for physicians, insurance companies, or specific procedures, peer review procedures, prospective system (PPS), appeals processes, rates for HMO services, regional adjustments, risk adjustment, reimbursement for chiropractors, foreign medical graduates, nurse practitioners, for outpatient services See also: 325 workforce training programs; 302 insurer or managed care consumer protections.')
    #add_document('bar', 'my name is bar')
    #print classify_document('To ensure that the fees that small businesses and other entities are charged for accepting debit cards are reasonable and proportional to the costs incurred, and to limit card networks from imposing anti-competitive restrictions on small businesses and other entities that accept cards.')
    #print similarity2('my name is foo and yeah this works','my name is bar and yeah this works')

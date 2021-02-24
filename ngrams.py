"""
Code taken from the chapter "Natural Language Corpus Data"
of the book "Beautiful Data" (Segaran and Hammerbacher, 2009)
http://oreilly.com/catalog/9780596157111/

Code copyright (c) 2008-2009 by Peter Norvig

You are free to use this code under the MIT licencse: 
http://www.opensource.org/licenses/mit-license.php
"""
import os.path
from math import log10

def memo(f):
    "Memoize function f."
    table = {}
    def fmemo(*args):
        if args not in table:
            table[args] = f(*args)
        return table[args]
    fmemo.memo = table
    return fmemo

class Pdist(dict):
    "A probability distribution estimated from counts in datafile."
    def __init__(self, data=[], N=None, missingfn=None):
        for key,count in data:
            self[key] = self.get(key, 0) + int(count)
        self.N = float(N or sum(self.itervalues()))
        self.missingfn = missingfn or (lambda k, N: 1./N)
    def __call__(self, key): 
        if key in self: return self[key]/self.N  
        else: return self.missingfn(key, self.N)

def datafile(name, sep='\t'):
    "Read key,value pairs from file."
    for line in open(os.path.join(os.path.dirname(__file__), name)):
        yield line.split(sep)

def avoid_long_words(key, N):
    "Estimate the probability of an unknown word."
    return 10./(N * 10**len(key))

N = 1024908267229 ## Number of tokens
Pw  = Pdist(datafile('count_1w.txt'), N, avoid_long_words)
P2w = Pdist(datafile('count_2w.txt'), N)

def combine(Pfirst, first, segment):
    "Combine first and rem results into one (probability, words) pair."
    (Prem, rem) = segment
    return Pfirst+Prem, [first]+rem 

def splits(text, L=20):
    "Return a list of all possible (first, rem) pairs, len(first)<=L."
    return [(text[:i+1], text[i+1:]) 
            for i in range(min(len(text), L))]

def cPw(word, prev):
    "Conditional probability of word, given previous word."
    try:
        return P2w[prev + ' ' + word]/float(Pw[prev])
    except KeyError:
        return Pw(word)

@memo
def segment2(text, prev='<S>'): 
    "Return (log P(words), words), where words is the best segmentation." 
    if not text: return 0.0, [] 
    candidates = [combine(log10(cPw(first, prev)), first, segment2(rem, first)) 
                  for first,rem in splits(text)] 
    return max(candidates) 


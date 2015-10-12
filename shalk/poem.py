import random

import pymongo as pym
import PoemTemplate as pt
from ngrams import Ngrams
from random import randint


class Poem():
    def __init__(self, type, db=None):
        self.ngrams = Ngrams(db)
        
        if type == 'haiku':
            self.pattern = ['*****', '*******', '*****']
            self.rs = '***'
            
        if type == 'tanka':
            self.pattern = ['*****', '*******', '*****', '*******', '*******']
            self.rs = '*****'
            
        if type == 'limerick':
            self.pattern = []
            self.rs = 'AABBA'
            lengths = []
            lengths.append(randint(8, 11))
            lengths.append(randint(8, 11))
            lengths.append(randint(5, 7))
            lengths.append(randint(5, 7))
            lengths.append(randint(8, 11))
            for length in lengths:
                self.pattern.append('*' * length)
                
        if type == 'quatrain':
            mean = randint(5, 12)
            lengths = []
            for x in range(0, 3):
                lengths.append(randint(mean-1, mean+1))
            for length in lengths:
                self.pattern.append('*' * length)
            #What we're doing now is giving the AAAA rhyme scene a 1/5 chance of happening
            p = randint(0,3)
            if p == 0:
                self.rs = 'AAAA'
            if p == 1:
                self.rs = 'AABB'
            if p == 2:
                self.rs = 'ABAB'
            if p == 3:
                self.rs = 'ABBA'
        if type == 'spenserian sonnet':
            mean = randint(7, 12)
            lengths = []
            for x in range(0, 13):
                lengths.append(randint(mean-1, mean+1))
            for length in lengths:
                self.pattern.append('*' * length)
            self.rs = 'ABABBCBCCDCDEE'
        if type == 'italian sonnet':
            mean = randint(7, 12)
            lengths = []
            for x in range(0, 13):
                lengths.append(randint(mean-1, mean+1))
            for length in lengths:
                self.pattern.append('*' * length)
            octave = 'ABBAABA'
            sestet = ''
            p = randint(0,3)
            if p == 0:
                sestet = 'CDCDCD'
            if p == 1:
                sestet= 'CDDCDC'
            if p == 2:
                sestet = 'CDECDE'
            if p == 3:
                sestet = 'CDECED'
            self.rs = octave + sestet
        if type == 'shakespearian sonnet':
            mean = randint(7, 12)
            lengths = []
            for x in range(0, 13):
                lengths.append(randint(mean-1, mean+1))
            for length in lengths:
                self.pattern.append('*' * length)
            self.rs = 'ABABCDCDEFEFGG'
                
        self.template = pt.PoemTemplate(self.pattern, self.rs)
        
        

    def generate(self):
        print "HOT NEW POEM COMING RIGHT UP:"
        template = self.template.createTemplate()

        syllables = [ i for x in template for i in x ]

        text = ''
        sylSum = 0
        currentLine = 0
        currentLineText = ''
        tuples = [(2, 'NOUN'), (1, 'VERB'), (2, 'NOUN'), (3, 'ADV'), (1, 'VERB'), (3, 'NOUN'), (2, 'NOUN'), (1, 'VERB'), (2, 'NOUN')]
        #DEVELOPMENT CHANGE:
        #for syl in syllables:
        for tuple in tuples:
            newestWord = self.nextWord(text, tuple)
            text += newestWord  + " "
            currentLineText += newestWord  + " "
            sylSum += tuple[0]
            if(sylSum == len(self.pattern[currentLine])):                
                print currentLineText
                currentLine += 1
                sylSum = 0
                currentLineText = ''
        return text

    def weightedChoice(self, choices):
        total = sum(w for c, w in choices)
        r = random.uniform(0, total)
        upto = 0
        for c, w in choices:
            if upto + w > r:
                return c
            upto += w
        assert False, "Shouldn't get here"

    #Abstraction of the repeated code in nextWord
    def weightedTuples(self, listOfNGrams, key, syl, multiplier=1):
        tuples = []
        for item in listOfNGrams:
            tuple = []
            tuple.append(item[key])
            tuple.append(multiplier * item[u'freq'])
            tuples.append(tuple)
        return tuples
    
    def smoothedGeneration(self, method, syl, unigrams, bigrams=[], trigrams=[], fourgrams=[]):
        if method == 'linear':
            multiplierUnigrams = 1
            multiplierBigrams = 50
            multiplerTrigrams = 200
            multiplierFourgrams = 1000
            tuples1 = self.weightedTuples(unigrams, u'word1', syl, multiplierUnigrams)
            tuples2 = self.weightedTuples(bigrams, u'word1', syl, multiplierBigrams)
            tuples3 = self.weightedTuples(trigrams, u'word2', syl, multiplerTrigrams)
            tuples4 = self.weightedTuples(fourgrams, u'word3', syl, multiplierFourgrams)
            return self.weightedChoice(tuples1+tuples2+tuples3+tuples4)
        if method == 'backoff':
            if(len(fourgrams) > 0):
                tuples4 = self.weightedTuples(fourgrams, u'word3', syl)
                return self.weightedChoice(tuples4)
            if(len(trigrams) > 0):
                tuples3 = self.weightedTuples(trigrams, u'word2', syl)
                return self.weightedChoice(tuples3)
            if(len(bigrams) > 0):
                tuples2 = self.weightedTuples(bigrams, u'word1', syl)
                return self.weightedChoice(tuples2)
            tuples1 = self.weightedTuples(unigrams, u'word1', syl)
            return self.weightedChoice(tuples1)
                

    #This is our ngram generating function.
    def nextWord(self, text, tuple):
        #Constants for the smoothing
        text = text[0:len(text)-1]
        words = text.split(" ")
        N = len(words)
        smoothing = 'backoff'
        unigrams = self.ngrams.find({"syllables" : tuple[0], "type" : tuple[1], "word2": {"$exists" : False}}, limit = 10   )
        if(N<=1):
            choice = self.smoothedGeneration(smoothing, tuple[0], unigrams)
            return choice
        bigrams = self.ngrams.find({"word0" : words[N-1], "syllables" : tuple[0], "type" : tuple[1], "word2": {"$exists" : False}}, limit = 10)
        if(N<=2):
            choice = self.smoothedGeneration(smoothing, tuple[0], unigrams, bigrams)
            return choice
        trigrams = self.ngrams.find({"word0" : words[N-2], "word1" : words[N-1], "syllables" : tuple[0], "type" : tuple[1], "word2": {"$exists" : True}, "word3": {"$exists" : False}}, limit = 10)
        if(N<=3):
            choice = self.smoothedGeneration(smoothing, tuple[0], unigrams, bigrams, trigrams)
            return choice
        fourgrams = self.ngrams.find({"word0" : words[N-3], "word1" : words[N-2], "word2" : words[N-1], "syllables" : tuple[0], "type" : tuple[1], "word3": {"$exists" : True}}, limit = 10)
        choice = self.smoothedGeneration(smoothing, tuple[0], unigrams, bigrams, trigrams, fourgrams)
        return choice

def main():
    p = Poem('haiku')
    for x in range(0, 20):
        p.generate()
    


if __name__ == "__main__":
    main()

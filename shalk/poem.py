import random

import pymongo as pym
import PoemTemplate as pt
from ngrams import Ngrams


class Poem():
    def __init__(self, pattern, db=None):
        self.ngrams = Ngrams(db)
        self.pattern = pattern
        self.template = pt.PoemTemplate(pattern, [])

    def generate(self):
        template = self.template.createTemplate()

        syllables = [ i for x in template for i in x ]

        text = ''
        for syl in syllables:
            text += self.nextWord(text, syl) + " "
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
    def nextWord(self, text, syl):
        #Constants for the smoothing
        text = text[0:len(text)-1]
        words = text.split(" ")
        N = len(words)
        smoothing = 'backoff'
        unigrams = self.ngrams.find({"syllables" : syl, "word2": {"$exists" : False}}, limit = 10   )
        if(N<=1):
            choice = self.smoothedGeneration(smoothing, syl, unigrams)
            return choice
        bigrams = self.ngrams.find({"word0" : words[N-1], "syllables" : syl, "word2": {"$exists" : False}}, limit = 10)
        if(N<=2):
            choice = self.smoothedGeneration(smoothing, syl, unigrams, bigrams)
            return choice
        trigrams = self.ngrams.find({"word0" : words[N-2], "word1" : words[N-1], "syllables" : syl, "word2": {"$exists" : True}, "word3": {"$exists" : False}}, limit = 10)
        if(N<=3):
            choice = self.smoothedGeneration(smoothing, syl, unigrams, bigrams, trigrams)
            return choice
        fourgrams = self.ngrams.find({"word0" : words[N-3], "word1" : words[N-2], "word2" : words[N-1], "syllables" : syl, "word3": {"$exists" : True}}, limit = 10)
        choice = self.smoothedGeneration(smoothing, syl, unigrams, bigrams, trigrams, fourgrams)
        return choice

def main():
    p = Poem(['*****', '*******', '*****'])
    for x in range(0, 50):
        print p.generate()
    


if __name__ == "__main__":
    main()

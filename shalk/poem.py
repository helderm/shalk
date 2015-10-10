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

    #This is our ngram generating function.
    def nextWord(self, text, syl):
        #Constants for the smoothing
        multiplierUnigrams = 1
        multiplierBigrams = 50
        multiplerTrigrams = 200
        multiplierFourgrams = 1000
        text = text[0:len(text)-1]
        words = text.split(" ")
        N = len(words)
        possible1grams = self.ngrams.find({"syllables" : syl, "word2": {"$exists" : False}}, limit = 9999)
        tuples1 = self.weightedTuples(possible1grams, u'word1', syl, multiplierUnigrams)
        if(N<=1):
            choice = self.weightedChoice(tuples1)
            return choice
        possible2grams = self.ngrams.find({"word0" : words[N-1], "syllables" : syl, "word2": {"$exists" : False}}, limit = 9999)
        tuples2 = self.weightedTuples(possible2grams, u'word1', syl, multiplierBigrams)
        if(N<=2):
            choice = self.weightedChoice(tuples1 + tuples2)
            return choice
        possible3grams = self.ngrams.find({"word0" : words[N-2], "word1" : words[N-1], "syllables" : syl, "word2": {"$exists" : True}, "word3": {"$exists" : False}}, limit = 9999)
        tuples3 = self.weightedTuples(possible3grams, u'word2', syl, multiplerTrigrams)
        if(N<=3):
            choice = self.weightedChoice(tuples1+tuples2+tuples3)
            return choice
        possible4grams = self.ngrams.find({"word0" : words[N-3], "word1" : words[N-2], "word2" : words[N-1], "syllables" : syl, "word3": {"$exists" : True}}, limit = 9999)
        tuples4 = self.weightedTuples(possible4grams, u'word3', syl, multiplierFourgrams)
        choice = self.weightedChoice(tuples1+tuples2+tuples3+tuples4)
        return choice
        #If we've reached this point, everything failed:

def main():
    p = Poem(['*****', '*******', '*****'])
    for x in range(0, 50):
        print p.generate()
    


if __name__ == "__main__":
    main()

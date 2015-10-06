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
    def weightedTuples(self, listOfNGrams, minLength, key, syl):
        tuples = []
        for item in listOfNGrams:
            tuple = []
            if (len(item) > minLength):
                tuple.append(item[key])
                tuple.append(item[u'freq'])
                tuples.append(tuple)
        return tuples

    #This is our ngram generating function.
    def nextWord(self, text, syl):
        text = text[0:len(text)-1]
        words = text.split(" ")
        N = len(words)
        print "current syllable target: " + str(syl)
        #First try 4 and 3 grams
        if(N >= 3):
            #First we attempt generating a word from the 4 gram corpus
            #possible4grams = list(db['ngrams'].find({"word0" : words[N-3], "word1" : words[N-2], "word2" : words[N-1], "syllables" : syl, 'word3': {'$exists' : True}}))
            possible4grams = self.ngrams.find({"word0" : words[N-3], "word1" : words[N-2], "word2" : words[N-1], "syllables" : syl, "word3": {"$exists" : True}})

            #This executes if there is any data                with "word0, word1, word2" as attributes, makes a weighted list of the word3's and returns
            #a weighted sample
            print "obb!" + str(len(possible4grams))
            if len(possible4grams) > 0:
                tuples = self.weightedTuples(possible4grams, 5, u'word3', syl)
                if(len(tuples) > 0):
                    choice = self.weightedChoice(tuples)
                    print "first"
                    print "Find a 4 gram word: " + str(choice)
                    return choice
        #Then we try 3 and 2 grams
        if(N>=2):
            #possible3grams = list(db['ngrams'].find({"word0" : words[N-2], "word1" : words[N-1], "syllables" : syl, 'word2': {'$exists' : True}, 'word3': {'$exists' : False}}))
            possible3grams = self.ngrams.find({"word0" : words[N-2], "word1" : words[N-1], "syllables" : syl, "word2": {"$exists" : True}, "word3": {"$exists" : False}})
            tuples = self.weightedTuples(possible3grams, 4, u'word2', syl)
            if len(possible3grams) > 0:
                if(len(tuples) > 0):
                    choice = self.weightedChoice(tuples)
                    print possible3grams
                    print "third"
                    print choice
                    return choice
        if(N>=1):
            #possible2grams = list(db['ngrams'].find({"word0" : words[N-1], "syllables" : syl, 'word2': {'$exists' : False}}))
            possible2grams = self.ngrams.find({"word0" : words[N-1], "syllables" : syl, "word2": {"$exists" : False}})
            tuples = self.weightedTuples(possible2grams, 3, u'word1', syl)
            if len(possible2grams) > 0:
                if(len(tuples) > 0):
                    choice = self.weightedChoice(tuples)
                    print possible2grams
                    print "fifth"
                    print choice
                    return choice
        #possible2grams = list(db['ngrams'].find({"syllables" : syl, 'word2': {'$exists' : False}}))
        possible2grams = self.ngrams.find({"syllables" : syl, "word2": {"$exists" : False}})
        tuples = self.weightedTuples(possible2grams, 3, u'word1', syl)
        if(len(tuples) > 0):
            choice = self.weightedChoice(tuples)
            print "sixth"
            print choice
            return choice
        #If we've reached this point, everything failed:
        return "random"

def main():
    p = Poem(['*****', '*******', '*****'])
    print p.generate()
    #this query finds all data that doesn't have a field from word3, i.e. 2grams and 3grams


if __name__ == "__main__":
    main()
#Do I only have 4 grams?
#in the database

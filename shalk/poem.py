import random

import pymongo as pym
import PoemTemplate as pt
from ngrams import Ngrams
from rhyme import RhymeScheme
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
        self.rhymesch = RhymeScheme(self.rs)
     

    def generate(self):
        print "HOT NEW POEM COMING RIGHT UP:"
        template = self.template.createTemplate()

        constraints = [ i for x in template for i in x ]

        text = ''
        sylSum = 0
        currentLine = 0
        currentLineText = ''
        for con in constraints:

            eol = (sylSum == len(self.pattern[currentLine]))

            newestWord = self.nextWord(text, con, eol)
            text += newestWord  + " "
            currentLineText += newestWord  + " "
            sylSum += con[0]
            if(sylSum == len(self.pattern[currentLine])):
                print currentLineText
                currentLine += 1
                sylSum = 0
                currentLineText = ''
        return text

    def weightedChoice(self, choices):
        total = sum(w for c, w, rhyme in choices)
        r = random.uniform(0, total)
        upto = 0
        for c, w, rhyme in choices:
            if upto + w > r:
                return c, rhyme
            upto += w
        assert False, "Shouldn't get here"

    #Abstraction of the repeated code in nextWord
    def weightedTuples(self, listOfNGrams, key, syl, multiplier=1):
        tuples = []
        for item in listOfNGrams:
            tuple = []
            tuple.append(item[key])
            tuple.append(multiplier * item[u'freq'])
            tuple.append(item['rhyme'])
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

    def nextWord(self, text, con, eol):
        #Constants for the smoothing
		#TODO: Catch the 'X' part of speech case
        text = text[0:len(text)-1]
        words = text.split(" ")
        N = len(words)
        smoothing = 'backoff'
        rhyming = False
        query = {}

        # if end of line, we need to add the rhyme constraint to the queries
        if eol and self.rhymesch:
            rhyming = True
            rhyme = self.rhymesch.get_curr_rhyme()
            if rhyme:
                query['rhyme'] = rhyme

        query = {"syllables" : con[0], "type" : con[1]}
        if rhyming and rhyme:
            query['rhyme'] = rhyme

        unigrams = self.ngrams.find(query, n=2, limit = 10 )

        if(N<=1):
            choice, rh = self.smoothedGeneration(smoothing, con[0], unigrams)
            if rhyming and not rhyme:
                self.rhymesch.add_rhyme(rh)
            return choice

        query = {"word0" : words[N-1], "syllables" : con[0], "type" : con[1]}
        if rhyming and rhyme:
            query['rhyme'] = rhyme

        bigrams = self.ngrams.find(query, n=2, limit = 10)

        if(N<=2):
            choice, rh = self.smoothedGeneration(smoothing, con[0], unigrams, bigrams)
            if rhyming and not rhyme:
                self.rhymesch.add_rhyme(rh)
            return choice

        query = {"word0" : words[N-2], "word1" : words[N-1], "syllables" : con[0], "type" : con[1] }
        if rhyming and rhyme:
            query['rhyme'] = rhyme

        trigrams = self.ngrams.find(query, n=3, limit = 10)
        if(N<=3):
            choice, rh = self.smoothedGeneration(smoothing, con[0], unigrams, bigrams, trigrams)
            if rhyming and not rhyme:
                self.rhymesch.add_rhyme(rh)
            return choice

        query = {"word0" : words[N-3], "word1" : words[N-2], "word2" : words[N-1], "syllables" : con[0], "type" : con[1]}
        if rhyming and rhyme:
            query['rhyme'] = rhyme

        fourgrams = self.ngrams.find(query, n=4, limit = 10)
        choice, rh = self.smoothedGeneration(smoothing, con[0], unigrams, bigrams, trigrams, fourgrams)

        if rhyming and not rhyme:
            self.rhymesch.add_rhyme(rh)
        return choice


def main():
    p = Poem('haiku')
    for x in range(0, 20):
        p.generate()



if __name__ == "__main__":
    main()

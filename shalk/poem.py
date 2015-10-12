import random

import pymongo as pym
import PoemTemplate as pt
from ngrams import Ngrams
from rhyme import RhymeScheme


class Poem():
    def __init__(self, pattern, rhymesch=None, db=None):
        self.ngrams = Ngrams(db)
        self.pattern = pattern
        self.template = pt.PoemTemplate(pattern, [])
        self.rhymesch = RhymeScheme(rhymesch) if rhymesch else None

    def generate(self):
        print "HOT NEW POEM COMING RIGHT UP:"
        template = self.template.createTemplate()

        syllables = [ i for x in template for i in x ]

        text = ''
        sylSum = 0
        currentLine = 0
        currentLineText = ''

        for syl in syllables:
            eol = (sylSum == ( len(self.pattern[currentLine]) - template[currentLine][-1] ) )
            newestWord = self.nextWord(text, syl, eol)
            text += newestWord  + " "
            currentLineText += newestWord  + " "
            sylSum += syl

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
    def nextWord(self, text, syl, eol):
        #Constants for the smoothing
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

        query = {"syllables" : syl}
        if rhyming and rhyme:
            query['rhyme'] = rhyme

        unigrams = self.ngrams.find(query, n=2, limit = 10 )

        if(N<=1):
            choice, rh = self.smoothedGeneration(smoothing, syl, unigrams)
            if rhyming and not rhyme:
                self.rhymesch.add_rhyme(rh)
            return choice

        query = {"word0" : words[N-1], "syllables" : syl}
        if rhyming and rhyme:
            query['rhyme'] = rhyme

        bigrams = self.ngrams.find(query, n=2, limit = 10)

        if(N<=2):
            choice, rh = self.smoothedGeneration(smoothing, syl, unigrams, bigrams)
            if rhyming and not rhyme:
                self.rhymesch.add_rhyme(rh)
            return choice

        query = {"word0" : words[N-2], "word1" : words[N-1], "syllables" : syl }
        if rhyming and rhyme:
            query['rhyme'] = rhyme

        trigrams = self.ngrams.find(query, n=3, limit = 10)
        if(N<=3):
            choice, rh = self.smoothedGeneration(smoothing, syl, unigrams, bigrams, trigrams)
            if rhyming and not rhyme:
                self.rhymesch.add_rhyme(rh)
            return choice

        query = {"word0" : words[N-3], "word1" : words[N-2], "word2" : words[N-1], "syllables" : syl}
        if rhyming and rhyme:
            query['rhyme'] = rhyme

        fourgrams = self.ngrams.find(query, n=4, limit = 10)
        choice, rh = self.smoothedGeneration(smoothing, syl, unigrams, bigrams, trigrams, fourgrams)

        if rhyming and not rhyme:
            self.rhymesch.add_rhyme(rh)

        return choice

def main():
    p = Poem(['*****', '*******', '*****'], rhymesch='ABA')
    for x in range(0, 50):
        p.generate()



if __name__ == "__main__":
    main()

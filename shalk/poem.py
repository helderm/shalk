import random

import pymongo as pym
import PoemTemplate as pt
from ngrams import Ngrams
from rhyme import RhymeScheme
from random import randint


class Poem():

    QUERY_LIMIT = 1024 * 4

    def __init__(self, ptype='haiku', smoothing='backoff', db=None):
        self.ngrams = Ngrams(db)
        self.type = ptype
        self.smoothing = smoothing
        self.pattern = []

        if self.type == 'haiku':
            self.pattern = ['*****', '*******', '*****']
            self.rs = None

        if self.type == 'tanka':
            self.pattern = ['*****', '*******', '*****', '*******', '*******']
            self.rs = None

        if self.type == 'limerick':
            self.rs = 'AABBA'
            lengths = []
            lengths.append(randint(8, 11))
            lengths.append(randint(8, 11))
            lengths.append(randint(5, 7))
            lengths.append(randint(5, 7))
            lengths.append(randint(8, 11))
            for length in lengths:
                self.pattern.append('*' * length)

        if self.type == 'quatrain':
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
        if self.type == 'spens_sonnet':
            mean = randint(7, 12)
            lengths = []
            for x in range(0, 13):
                lengths.append(randint(mean-1, mean+1))
            for length in lengths:
                self.pattern.append('*' * length)
            self.rs = 'ABABBCBCCDCDEE'
        if self.type == 'ital_sonnet':
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
        if self.type == 'shaks_sonnet':
            mean = randint(7, 12)
            lengths = []
            for x in range(0, 13):
                lengths.append(randint(mean-1, mean+1))
            for length in lengths:
                self.pattern.append('*' * length)
            self.rs = 'ABABCDCDEFEFGG'

        self.template = pt.PoemTemplate(self.pattern, self.rs)


    def generate(self):
        """
        Generates a new poem with a new rhyming and template
        """

        rhymesch = RhymeScheme(self.rs) if self.rs else None
        sentences = self.template.createTemplate()
        while len(sentences) == 0:
            sentences = self.template.createTemplate()

        text = ''
        chosen_words = []
        for sentence in sentences:
            for word in sentence:
                if not isinstance(word, pt.Word):
                    # if not Word, is a punctuation
                    text = text[:-1] + word + ' '
                    continue

                word.text = self._next_word(chosen_words, word, rhymesch)
                if not word.text or not len(word.text):
                    # TODO: throw this SENTENCE away, not the entire poem!!!
                    return

                text += word.text + ' '
                chosen_words.append(word)

            text += '\n'

        text = text[:-2] + '.\n'
        return text

    def _weighted_choice(self, choices):
        total = sum(w for c, w, rhyme in choices)
        r = random.uniform(0, total)
        upto = 0
        for c, w, rhyme in choices:
            if upto + w > r:
                return c, rhyme
            upto += w
        return [], []

    #Abstraction of the repeated code in nextWord
    def _weighted_tuples(self, listOfNGrams, key, syl, multiplier=1):
        tuples = []
        for item in listOfNGrams:
            tuple = []
            tuple.append(item[key])
            tuple.append(multiplier * item[u'freq'])
            tuple.append(item['rhyme'])
            tuples.append(tuple)
        return tuples

    def _smoothed_generation(self, syl, unigrams, bigrams=[], trigrams=[], fourgrams=[]):
        if self.smoothing == 'linear':
            multiplierUnigrams = 1
            multiplierBigrams = 50
            multiplerTrigrams = 200
            multiplierFourgrams = 1000
            tuples1 = self._weighted_tuples(unigrams, u'word1', syl, multiplierUnigrams)
            tuples2 = self._weighted_tuples(bigrams, u'word1', syl, multiplierBigrams)
            tuples3 = self._weighted_tuples(trigrams, u'word2', syl, multiplerTrigrams)
            tuples4 = self._weighted_tuples(fourgrams, u'word3', syl, multiplierFourgrams)
            return self._weighted_choice(tuples1+tuples2+tuples3+tuples4)
        if self.smoothing == 'backoff':
            if(len(fourgrams) > 0):
                tuples4 = self._weighted_tuples(fourgrams, u'word3', syl)
                return self._weighted_choice(tuples4)
            if(len(trigrams) > 0):
                tuples3 = self._weighted_tuples(trigrams, u'word2', syl)
                return self._weighted_choice(tuples3)
            if(len(bigrams) > 0):
                tuples2 = self._weighted_tuples(bigrams, u'word1', syl)
                return self._weighted_choice(tuples2)
            tuples1 = self._weighted_tuples(unigrams, u'word1', syl)
            if (len(unigrams) > 0):
                tuples1 = self._weighted_tuples(unigrams, u'word1', syl)
                return self._weighted_choice(tuples1)

        return [], []

    #This is our ngram generating function.
    def _next_word(self, words, nextword, rhymesch):
        #Constants for the smoothing
		#TODO: Catch the 'X' part of speech case
        N = len(words)
        query = {}

        # if end of line, we need to add the rhyme constraint to the queries
        if nextword.rhyme != '*' and rhymesch:
            rhyme = rhymesch.get_rhyme(nextword.rhyme)
            query['rhyme'] = rhyme

        query['syllables'] = nextword.syllables
        query['type'] = nextword.typespeech
        unigrams = self.ngrams.find(query, n=2, limit=Poem.QUERY_LIMIT)

        if(N<=1):
            choice, rh = self._smoothed_generation(nextword.syllables, unigrams)
            if len(choice) == 0:
                return []
            return choice

        query['word0'] = words[N-1].text
        bigrams = self.ngrams.find(query, n=2, limit=Poem.QUERY_LIMIT)

        if(N<=2):
            choice, rh = self._smoothed_generation(nextword.syllables, unigrams, bigrams)
            return choice

        query['word0'] = words[N-2].text
        query['word1'] = words[N-1].text
        trigrams = self.ngrams.find(query, n=3, limit=Poem.QUERY_LIMIT)
        if(N<=3):
            choice, rh = self._smoothed_generation(nextword.syllables, unigrams, bigrams, trigrams)
            return choice

        query['word0'] = words[N-3].text
        query['word1'] = words[N-2].text
        query['word2'] = words[N-1].text
        fourgrams = self.ngrams.find(query, n=4, limit=Poem.QUERY_LIMIT)
        choice, rh = self._smoothed_generation(nextword.syllables, unigrams, bigrams, trigrams, fourgrams)

        return choice

def main():
    p = Poem()
    for x in range(0, 100):
        print "*** HOT NEW POEM COMING RIGHT UP!!! ***"
        text = p.generate()
        if not text:
            print "Yeah, not this time... Let me try again!"
            continue

        print text

if __name__ == "__main__":
    main()

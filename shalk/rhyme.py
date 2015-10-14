import random

class RhymeScheme(object):

    GOOD_RHYMES = ['AH0ND', 'ER0', 'AE1T', 'IY1', 'AH0L', 'IH0NG', 'IY0', 'AH0N', 'AH0L', 'AH0', 'UW1', 'AH1V']

    def __init__(self, pattern):
        self.pattern = pattern
        self.curr_rhyme = 0
        self.rhymes = {}

    def get_rhyme(self, rtype):
        if rtype not in self.rhymes:
            used_rhymes = [ i for k, i in self.rhymes.iteritems() ]
            possib_rhymes = [ i for i in RhymeScheme.GOOD_RHYMES if i not in used_rhymes ]
            self.rhymes[rtype] = random.choice(possib_rhymes)

        return self.rhymes.get(rtype)

    def add_rhyme(self, rvalue):
        rtype = self.pattern[self.curr_rhyme-1]

        self.rhymes[rtype] = rvalue

    def get_curr_rhyme(self, rtype):
        rtype = self.pattern[self.curr_rhyme]

        self.curr_rhyme += 1
        if self.curr_rhyme >= len(self.pattern):
            self.curr_rhyme = 0

        return self.rhymes.get(rtype, None)








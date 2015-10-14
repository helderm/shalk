import random

class RhymeScheme(object):

    def __init__(self, pattern):
        self.pattern = pattern
        self.curr_rhyme = 0
        self.rhymes = {}

        self.good_rhymes = ['AH0ND', 'ER0', 'AE1T', 'IY1', 'AH0L', 'IH0NG']

    def get_rhyme(self, rtype):
        if rtype not in self.rhymes:
            self.rhymes[rtype] = random.choice(self.good_rhymes)

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








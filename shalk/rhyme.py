

class RhymeScheme(object):

    def __init__(self, pattern):
        self.pattern = pattern
        self.curr_rhyme = 0
        self.rhymes = {}

    def get_rhyme(self, rtype):
        return self.rhymes.get(rtype, None)

    def add_rhyme(self, rvalue):
        rtype = self.pattern[self.curr_rhyme-1]

        self.rhymes[rtype] = rvalue

    def get_curr_rhyme(self):
        rtype = self.pattern[self.curr_rhyme]

        self.curr_rhyme += 1
        if self.curr_rhyme >= len(self.pattern):
            self.curr_rhyme = 0

        return self.rhymes.get(rtype, None)








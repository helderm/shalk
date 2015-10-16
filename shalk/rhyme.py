import random

class RhymeScheme(object):
    """ Class responsible for associating each ryme type (A, B, C) with its
         corresponding database representation
    """

    # these rhymes are know to be frequent in our database
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

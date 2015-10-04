import numpy as np


class PoemTemplate:

    """ This class expects the structure of a poem.
        metricPattern should be a list of strings, each string corresponding to the syllables in one line.
        Use 's' for stressed, 'w' for unstressed and '*' for blanks. Currently only working for total amount.
        rhymeScheme is currently not implemented.
        You can also passed predefined types of poems (TODO: add more).
    """
    haiku = ['*****', '*******', '*****']
    averageSyllablesPerWord = 2;
    standardDerivation = 1;

    def __init__(self, mP, rS):
        self.metricPattern = mP
        self.rhymeScheme = rS

    def createTemplate(self):
        temp = []
        # for each line
        for s in self.metricPattern:
            line = []
            lineLength = len(s)
            while lineLength > 0:
                syllables = round(np.random.normal(self.averageSyllablesPerWord, self.standardDerivation))
                syllables =  min(syllables, lineLength)

                if (syllables > 0):
                    line.append(syllables)
                lineLength -= syllables

            temp.append(line)
        return temp




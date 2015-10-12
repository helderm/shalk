import numpy as np
import pickle
import scipy.stats as stats
import random


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
        self.grammar = pickle.load(open("grammar", "rb"))
        self.grammarDistribution = [len(i) for i in self.grammar]
        self.metricPattern = mP
        self.rhymeScheme = rS


    def createTemplate(self):

        ## generate the metric template
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

        ## generate grammar tempate
        word_count = 0
        for l in temp:
            for w in l:
                word_count = word_count + 1

        all_sents = []
        all_len = []
        while word_count > 0:

            partition = sum(self.grammarDistribution)
            normalized_distribution = [float(x) / partition for x in self.grammarDistribution]

            dis = stats.rv_discrete(name='dis', values=(range(len(self.grammarDistribution)), normalized_distribution))
            sentence_length = dis.rvs(size=1)
            all_len.append(sentence_length[0])

            word_count = word_count - sentence_length

        if word_count < 0:
            for i in range(abs(word_count)):
                possible_choices = np.where(np.asarray(all_len) > 2)[0]
                choice = random.choice(possible_choices)
                all_len[choice] = all_len[choice] - 1


        for i in range(len(all_len)):
           all_sents.append(random.choice(self.grammar[all_len[i]]))

        all_sents = [i for sl in all_sents for i in sl]

        i = 0
        final_template = []
        for j, l in enumerate(temp):
            final_template.append([])
            for w in l:
                if all_sents[i] == ".":
                    i = i+1
                final_template[j].append([w, all_sents[i]])
                i = i + 1


        print(final_template)
        return final_template




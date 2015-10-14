import numpy as np
import pickle
import random



class PoemTemplate:

    """ This class expects the structure of a poem.
        metricPattern should be a list of strings, each string corresponding to the syllables in one line.
        Use 's' for stressed, 'w' for unstressed and '*' for blanks. Currently only working for total amount.
        rhymeScheme is currently not implemented.
        You can also passed predefined types of poems (TODO: add more).
    """
    haiku = ['*****', '*******', '*****']
    averageSyllablesPerWord = 1.5;
    standardDerivation = 0.5;

    def __init__(self, mP, rhyme_pattern):
        self.grammar = pickle.load(open("grammar", "rb"))
        self.grammarDistribution = [len(i) for i in self.grammar]
        self.metricPattern = mP
        self.rhyme_pattern = rhyme_pattern
        self.punctuations = []


    def createTemplate(self):
        self.punctuations = []
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


            p = random.random()
            sentence_length = 0
            sum_p = 0
            while sum_p < p:
                sum_p = sum_p + normalized_distribution[sentence_length]
                sentence_length = sentence_length + 1

            all_len.append(sentence_length)

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
        for s in all_sents:
            if s == ".":
                self.punctuations.append(i-1)
                i = i -1
            i = i+1

        i = 0
        final_template = []
        for j, l in enumerate(temp):
            final_template.append([])
            for w in l:
                if all_sents[i] == ".":
                    i = i+1
                final_template[j].append([w, all_sents[i]])
                i = i + 1

        # convert the old list-of-lists format the new one
        sentences = []
        word_count = 0
        rhyme_counter = 0
        for sentence in final_template:
            words = []
            for word in sentence:
                if word_count > self.punctuations[0]:
                    words.append('.')
                    self.punctuations = self.punctuations[1:]

                w = Word(syllables=word[0], typespeech=word[1])
                words.append(w)
                word_count += 1

            if self.rhyme_pattern:
                words[-1].rhyme = self.rhyme_pattern[rhyme_counter]
                rhyme_counter += 1

            s = Sentence(words)
            sentences.append(s)

        return sentences

class Sentence(object):
    def __init__(self, words):
        self.words = words

    def __repr__(self):
        strs = [ str(i) for i in self.words ]
        return ', '.join(strs)

    def __iter__(self):
        return iter(self.words)

class Word(object):
    def __init__(self, syllables, typespeech, rhyme='*'):
        self.syllables = syllables
        self.typespeech = typespeech
        self.rhyme = rhyme
        self.text = None

    def __str__(self):
        return 'A {0} syllables {1}'.format(self.syllables, self.typespeech.lower())

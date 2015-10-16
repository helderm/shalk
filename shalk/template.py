import numpy as np
import pickle
import random
import os

class PoemTemplate(object):
    """ This class represents the structure of a poem
        metricPattern should be a list of strings, each string corresponding to the syllables in one line.
    """
    averageSyllablesPerWord = 1.5;
    standardDerivation = 0.5;

    def __init__(self, mP, rhyme_pattern):
        this_dir, this_filename = os.path.split(__file__)
        grammar_file = os.path.join(this_dir, "data", "grammar.dat")
        self.grammar = pickle.load(open(grammar_file, "rb"))

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
            syllables_last_word = round(np.random.normal(self.averageSyllablesPerWord, self.standardDerivation))
            syllables_last_word =  max(2.0, syllables_last_word)

            lineLength = lineLength - syllables_last_word
            while lineLength > 0:
                syllables = round(np.random.normal(self.averageSyllablesPerWord, self.standardDerivation))
                syllables =  min(syllables, lineLength)

                if (syllables > 0):
                    line.append(syllables)
                lineLength -= syllables
            line.append(syllables_last_word)
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


        # save line endings
        line_endings = []
        line_sum = 0

        line_sum = 0
        for l in temp:

            for w in l:
                line_sum = line_sum + 1
            line_endings.append(line_sum)

        sentence_sum = 0
        for i in range(len(all_len)):
            sent_range = range(sentence_sum+1, sentence_sum + all_len[i]+1)
            sentence_sum = sentence_sum + all_len[i]
            intersection_list = [v for v in sent_range if v in line_endings]
            # restrict list to sentences that have verbs or noun at the end of line
            restricted_list = []
            for s in self.grammar[all_len[i]]:
                s_without_punct = []
                for w in s:
                    if not w == ".":
                        s_without_punct.append(w)
                all_true = True
                for r in intersection_list:
                    if not (s_without_punct[(r-(sentence_sum-all_len[i]))-1] == 'VERB' or s_without_punct[(r-(sentence_sum-all_len[i]))-1] == 'NOUN'):
                        all_true = False
                if all_true:
                    restricted_list.append(s)
            if len(restricted_list) == 0:
                return []
            all_sents.append(random.choice(restricted_list))

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

            # append words to the sentence
            for word in sentence:
                if word_count > self.punctuations[0]:
                    words.append(',')
                    self.punctuations = self.punctuations[1:]

                w = Word(syllables=word[0], typespeech=word[1])
                words.append(w)
                word_count += 1

            # add the rhyme at the end of the sentence
            if self.rhyme_pattern:
                words[-1].rhyme = self.rhyme_pattern[rhyme_counter]
                rhyme_counter += 1

            # fix punctuation position and type
            if not isinstance(words[0], Word):
                words = words[1:]
                if len(sentences) and isinstance(sentences[-1].words[-1], Word):
                    sentences[-1].words.append('.')
            if not isinstance(words[-1], Word):
                words[-1] = '.'

            s = Sentence(words)
            sentences.append(s)

        return sentences

class Sentence(object):
    """ List of words and punctuation in a line """
    def __init__(self, words):
        self.words = words

    def __repr__(self):
        strs = [ str(i) for i in self.words ]
        return ', '.join(strs)

    def __iter__(self):
        return iter(self.words)

class Word(object):
    """ Representation of a word.
        Initially it contains only the set of contraints for the database query.
        Later it will be feedes with the chosen word for that set of contraints
    """
    def __init__(self, syllables, typespeech, rhyme='*'):
        self.syllables = syllables
        self.typespeech = typespeech
        self.rhyme = rhyme
        self.text = None

    def __repr__(self):
        return str(self)

    def __str__(self):
        if self.text:
            return self.text
        return 'A {0} syllables {1}{2}'.format(self.syllables, self.typespeech.lower(), ' '+self.rhyme if self.rhyme != '*' else '')

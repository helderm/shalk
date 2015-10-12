import nltk
import numpy as np
from nltk.corpus import gutenberg
import pickle


def save_object(obj, filename):
    with open(filename, 'w') as output:
        pickle.dump(obj, output, pickle.HIGHEST_PROTOCOL)

sents = gutenberg.sents('blake-poems.txt')

table = []
for i in range(20):
    table.append([])
for s in sents[1:]:
    # TODO prevent ?!, => . and dont count . in a sentence to length
    if len(s) > 2 and len(s) < 20:
        tags = nltk.pos_tag(s)
        simpleTags = [(word, nltk.map_tag('en-ptb', 'universal', tag)) for word, tag in tags]
        tagsOnly = [t[1] for t in simpleTags]
        # this is to filter out headlines
        if (tagsOnly[len(tagsOnly)-1] == "."):
            wordCount = len(tagsOnly) - tagsOnly.count(".")
            table[wordCount].append(tagsOnly)

save_object(table, "grammar")
#!/usr/bin/env python

import pymongo as pym

import os, sys
import nltk
from nltk.corpus import cmudict
from nltk.tag import pos_tag, map_tag

EXP_DOC_COUNT = 0

def main():

    print '* Executing database import procedure...'

    mongodb_url = os.getenv('OPENSHIFT_MONGODB_DB_URL')

    print '* Connecting to [{0}]...'.format(mongodb_url)

    client = pym.MongoClient(mongodb_url)
    db = client['shalk']

    # if we have data already, do nothing
    #if db['ngrams'].count() > EXP_DOC_COUNT:
    #    print '* Database already has data, aborting import procedure.'
    #   return'''

    #cleans the collection and start importing again
    db['ngrams'].drop()

    # import files into db
    base_data_dir = os.getenv('OPENSHIFT_DATA_DIR')
    if not base_data_dir:
        base_data_dir = '../data/'

    #
    nltk.data.path = [ '{0}nltk/'.format(base_data_dir) ]
    cdict = cmudict.dict()

    files = [ '{0}ngrams/w2_.txt'.format(base_data_dir),
              '{0}ngrams/w3_.txt'.format(base_data_dir),
              '{0}ngrams/w4_.txt'.format(base_data_dir) ]

    for datafile in files:
        load_file_into_db(db, datafile, cdict)

    print '* Database import finished!'

def load_file_into_db(db, datafile, cdict):

    print '* Importing file [{0}] into db...'.format(datafile)

    count = 0
    mod = 10000
    with open(datafile, 'r') as f:
        ngrams = []
        for line in f:
            parts = line.rstrip().split('\t')

            ngram = {}
            ngram['freq'] = int(parts[0])
            insert = True
            syllables = 0
            for i, word in enumerate(parts[1:]):
                # if a word has no entry in the cmu dictionary -> don't insert
                syllables = count_syllables(word, cdict)
                if not syllables:
                    insert = False
                    break

                # added num syllables
                ngram['syllables'] = syllables

                # add word
                key = 'word{0}'.format(i)
                ngram[key] = word.decode('utf-8', 'ignore')

            if not insert:
                continue

            # add the type of the last word
            wtype = get_last_word_types(line.rstrip().replace('\t', ' ').decode('utf-8', 'ignore'))
            ngram['type'] = wtype

            ngrams.append(ngram)
            count += 1
            if count % mod == 0:
                print '- Inserted [{0}] ngrams into db...'.format(len(ngrams) * (count / mod))
                sys.stdout.flush()
                db['ngrams'].insert_many(ngrams)
                ngrams = []

    print '- Inserting [{0}] ngrams into db...'.format(len(ngrams))
    sys.stdout.flush()
    db['ngrams'].insert_many(ngrams)

    print '* Finished importing file [{0}]!'.format(datafile)


def get_last_word_types(ngram):
    text = nltk.word_tokenize(ngram)
    posTagged = pos_tag(text)
    lastword_tag = map_tag('en-ptb', 'universal', posTagged[-1][1])
    #simplifiedTags = [(word, map_tag('en-ptb', 'universal', tag)) for word, tag in posTagged]

    return lastword_tag


def count_syllables(word, cdict):
        word = word.lower()

        if word not in cdict:
                return 0
        else:
            return sum(l.isdigit() for s in cdict[word][0] for l in s)

if __name__ == '__main__':
    main()


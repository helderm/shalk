#!/usr/bin/env python

import pymongo as pym

import os, sys
from nltk.corpus import cmudict

EXP_DOC_COUNT = 0
d = cmudict.dict()


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
    data_dir = os.getenv('')
    files = [ '../data/w2_.txt'.format(data_dir),
              '../data/w3_.txt'.format(data_dir),
              '../data/w4_.txt'.format(data_dir) ]

    for datafile in files:
        load_file_into_db(db, datafile)

    print '* Database import finished!'

def countSyllables(word):
        word = word.lower()
        if word not in d:
                return 0
        else:
            return sum(l.isdigit() for s in d[word][0] for l in s)

def load_file_into_db(db, datafile):

    print '* Importing file [{0}] into db...'.format(datafile)

    count = 0
    mod = 100000
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
                syllables = countSyllables(word)
                if not syllables:
                    insert = False
                    break
                else:
                    ngram['syllables'] = syllables
                key = 'word{0}'.format(i)
                ngram[key] = word.decode('utf-8', 'ignore')


            '''ngrams.append(ngram)

            count += 1
            if count % mod == 0:
                print '- Inserting [{0}] ngrams into db...'.format(len(ngrams))
    		    sys.stdout.flush()
                db['ngrams'].insert_many(ngrams)
		        ngrams = []
               db['ngrams'].insert_many(ngrams)'''

            if insert:
                ngrams.append(ngram)

    print '- Inserting [{0}] ngrams into db...'.format(len(ngrams))
    sys.stdout.flush()
    db['ngrams'].insert_many(ngrams)

    print '* Finished importing file [{0}]!'.format(datafile)


if __name__ == '__main__':
    main()


#!/usr/bin/env python

import pymongo as pym
import os

EXP_DOC_COUNT = 20000000

def main():

    print '* Executing database import procedure...'

    mongodb_url = os.getenv('OPENSHIFT_MONGODB_DB_URL')

    print '* Connecting to [{0}]...'.format(mongodb_url)

    client = pym.MongoClient(mongodb_url)
    db = client['shalk']

    # if we have data already, do nothing
    if db['ngrams'].count() > EXP_DOC_COUNT:
        print '* Database already has data, aborting import procedure.'
        return

    # cleans the collection and start importing again
    db['ngrams'].drop()

    # import files into db
    data_dir = os.getenv('OPENSHIFT_DATA_DIR')
    files = [ '{0}/ngrams/w2_.txt'.format(data_dir),
              '{0}/ngrams/w3_.txt'.format(data_dir),
              '{0}/ngrams/w4_.txt'.format(data_dir) ]

    for datafile in files:
        load_file_into_db(db, datafile)

    print '* Database import finished!'


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
            for i, word in enumerate(parts[1:]):
                key = 'word{0}'.format(i)
                ngram[key] = word.decode('utf-8', 'ignore')

            ngrams.append(ngram)

            count += 1
            if count % mod == 0:
                print '- Inserting [{0}] ngrams into db...'.format(len(ngrams))
                db['ngrams'].insert_many(ngrams)

            #ngrams.append(ngram)

    print '- Inserting [{0}] ngrams into db...'.format(len(ngrams))
    db['ngrams'].insert_many(ngrams)

    print '* Finished importing file [{0}]!'.format(datafile)


if __name__ == '__main__':
    main()


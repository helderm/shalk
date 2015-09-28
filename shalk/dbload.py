#!/usr/bin/env python

import pymongo as pym
import os

def main():

    print '* Executing database import procedure...'

    mongodb_url = os.getenv('OPENSHIFT_MONGODB_DB_URL')

    print '* Connecting to [{0}]...'.format(mongodb_url)

    client = pym.MongoClient(mongodb_url)
    db = client['shalk']

    # if we have data already, do nothing
    if db['ngrams'].count() > 0:
        print '* Database already has data, aborting import procedure.'
        return

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

            db['ngrams'].insert_one(ngram)

            count += 1
            if count % mod == 0:
                print '- Inserted [{0}] documents...'.format((count / mod) * mod )
            #ngrams.append(ngram)

    print '* Finished importing file [{0}]!'.format(datafile)
    #print '* Inserting [{0}] ngrams into db...'.format(len(ngrams))
    #db['ngrams'].insert_many(ngrams)


if __name__ == '__main__':
    main()


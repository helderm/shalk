#!/usr/bin/env python

import pymongo as pym
import os, sys
import nltk
from nltk.corpus import cmudict
from nltk.tag import pos_tag, map_tag
from joblib import Parallel, delayed
import argparse
import traceback
import time


EXP_DOC_COUNT = 1 * 1000 * 1000

def main():

    # parse args
    parser = argparse.ArgumentParser(prog='dbload', description='Shalk database loading script')
    parser.add_argument('-r', '--recover', help='Recover mode', action='store_true')
    parser.add_argument('-f', '--force', help='Force the database loading. This will destroy the db and create one from scratch!!', action='store_true')

    args = parser.parse_args()

    if args.recover:
        recover_db()
        return

    print '* Executing database import procedure...'

    mongodb_url = os.getenv('OPENSHIFT_MONGODB_DB_URL')

    print '* Connecting to [{0}]...'.format(mongodb_url)

    client = pym.MongoClient(mongodb_url)
    db = client['shalk']

    # if we have data already, do nothing
    if not args.force and db['ngrams'].count() > EXP_DOC_COUNT:
        print '* Database already has data, aborting import procedure.'
        return

    #cleans the collection and create indexes
    db['ngrams'].drop()
    db['ngrams'].create_index([( 'syllables', pym.ASCENDING ),
                       ( 'word0', pym.ASCENDING ),
                       ( 'word1', pym.ASCENDING )])

    # import files into db
    base_data_dir = os.getenv('OPENSHIFT_DATA_DIR')
    if not base_data_dir:
        base_data_dir = '../data/'

    files = [ '{0}ngrams/w2_.txt'.format(base_data_dir),
              '{0}ngrams/w3_.txt'.format(base_data_dir),
              '{0}ngrams/w4_.txt'.format(base_data_dir)]

    #for df in files:
    #    load_file_into_db(df)

    # run each file import in parallel
    Parallel(n_jobs=len(files))(delayed(load_file_into_db)(datafile) for datafile in files)

    print '* Database import finished!'

def load_file_into_db(datafile):

    filename = datafile.rsplit('/')[-1]
    print '* Importing file [{0}] into db...'.format(filename)

    # connect to db
    mongodb_url = os.getenv('OPENSHIFT_MONGODB_DB_URL')
    client = pym.MongoClient(mongodb_url)
    db = client['shalk']
    coll = db['ngrams']

    base_data_dir = os.getenv('OPENSHIFT_DATA_DIR')
    if not base_data_dir:
        base_data_dir = '../data/'

    # initialize cmu dict
    nltk.data.path = [ '{0}nltk/'.format(base_data_dir) ]
    cdict = cmudict.dict()

    count = 0
    mod = 10000
    with open(datafile, 'r') as f:
        ngrams = []
        for line in f:
            ngram = get_ngram(line, cdict)

            if not ngram:
                continue

            ngrams.append(ngram)
            count += 1
            if count % mod == 0:
                print '- ({0}) Inserted [{1}] ngrams into db...'.format(filename, len(ngrams) * (count / mod))
                sys.stdout.flush()
                insert_ngrams(ngrams, coll)
                ngrams = []

    print '- ({0}) Inserting last [{1}] ngrams into db...'.format(filename, len(ngrams))
    sys.stdout.flush()
    insert_ngrams(ngrams, coll)

    print '* Finished importing file [{0}]!'.format(filename)

def recover_db():
    print '* Executing database RECOVERY procedure...'

    # import files into db
    base_data_dir = os.getenv('OPENSHIFT_DATA_DIR')
    if not base_data_dir:
        base_data_dir = '../data/'

    files = [ '{0}ngrams/w2_.txt'.format(base_data_dir),
              '{0}ngrams/w3_.txt'.format(base_data_dir),
              '{0}ngrams/w4_.txt'.format(base_data_dir)]

    for df in files:
        recover_file_to_db(df)

def recover_file_to_db(datafile):

    filename = datafile.rsplit('/')[-1]
    print '* Recovering file [{0}] into db...'.format(filename)

    # connect to db
    mongodb_url = os.getenv('OPENSHIFT_MONGODB_DB_URL')
    client = pym.MongoClient(mongodb_url)
    db = client['shalk']
    coll = db['ngrams']

    base_data_dir = os.getenv('OPENSHIFT_DATA_DIR')
    if not base_data_dir:
        base_data_dir = '../data/'

    # initialize cmu dict
    nltk.data.path = [ '{0}nltk/'.format(base_data_dir) ]
    cdict = cmudict.dict()

    count = 0
    mod = 1

    # open file in reverse, and import it until we find the point where we stopped
    ngrams = []
    for line in reversed(open(datafile).readlines()):
        ngram = get_ngram(line, cdict)

        if not ngram:
            continue

        # stop we find this ngram in the db already
        if coll.find_one(ngram):
            print '- ({0}) Ngram [{1}] already in the db, stopping recovery!'
            sys.stdout.flush()
            return

        ngrams.append(ngram)
        count += 1
        if count % mod == 0:
            print '- ({0}) Inserted [{1}] ngrams into db...'.format(filename, len(ngrams) * (count / mod))
            print '- ({0}) {1} -> {2}'.format(filename, ngrams[0], ngrams[-1])
            sys.stdout.flush()
            insert_ngrams(ngrams, coll)
            ngrams = []

    print '- ({0}) Inserting last [{1}] ngrams into db...'.format(filename, len(ngrams))
    sys.stdout.flush()
    insert_ngrams(ngrams, coll)

    print '* Finished importing file [{0}]!'.format(filename)

def get_ngram(line, cdict):
    ngram = {}

    parts = line.rstrip().split('\t')

    syllables = 0
    try:
        for i, word in enumerate(parts[1:]):
            # if a word has no entry in the cmu dictionary -> don't insert
            syllables = count_syllables(word, cdict)
            if not syllables:
                return None

            # added num syllables
            ngram['syllables'] = syllables

            # add word
            key = 'word{0}'.format(i)
            ngram[key] = word.decode('utf-8', 'ignore')

        # add frequency
        ngram['freq'] = int(parts[0])

        # add the type of the last word
        wtype = get_last_word_types(' '.join(parts[1:]))
        ngram['type'] = wtype

    except Exception as e:
        print 'ERROR while parsing ngram [{0}]! Ignoring it...'.format(line)
        print traceback.format_exc()
        sys.stdout.flush()
        return None

    return ngram


def insert_ngrams(ngrams, coll):
    tries = 5

    while tries:
        try:
            coll.insert_many(ngrams)
            break
        except Exception as e:
            print 'ERROR while inserting ngrams into db! Trying {0} more times...'.format(tries)
            print traceback.format_exc()
            sys.stdout.flush()
            time.sleep(tries * 5)
            tries -= 1

    if not tries:
        print 'ERROR while adding ngram from {0} to {1}'.format(ngrams[0], ngrams[-1])
        raise Exception('Failed to add ngrams!')

def get_last_word_types(ngram):
    text = nltk.word_tokenize(ngram)
    posTagged = pos_tag(text)
    lastword_tag = map_tag('en-ptb', 'universal', posTagged[-1][1])

    return lastword_tag


def count_syllables(word, cdict):
        word = word.lower()

        if word not in cdict:
                return 0
        else:
            return sum(l.isdigit() for s in cdict[word][0] for l in s)

if __name__ == '__main__':
    main()


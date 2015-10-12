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
import random
import re


EXP_DOC_COUNT = 1 * 1000 * 1000
args = None

def main():

    # parse args
    parser = argparse.ArgumentParser(prog='dbload', description='Shalk database loading script')
    parser.add_argument('-m', '--mode', help='Script mode', choices=['recover', 'load', 'fix'], default='load')
    parser.add_argument('-f', '--force', help='Force the database loading', action='store_true')
    parser.add_argument('-s', '--split', help='Split the ngrams into different collections', action='store_true')

    global args
    args = parser.parse_args()

    # execute recover db procedure
    if args.mode == 'recover':
        recover_db()
        return
    elif args.mode == 'fix':
        fix_db()
        return

    load_db()


def load_db():

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
    create_collections(db)

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
                insert_ngrams(ngrams, db)
                ngrams = []

    print '- ({0}) Inserting last [{1}] ngrams into db...'.format(filename, len(ngrams))
    sys.stdout.flush()
    insert_ngrams(ngrams, db)

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
    mod = 1000

    # open file in reverse, and import it until we find the point where we stopped
    ngrams = []
    for line in reversed(open(datafile).readlines()):
        ngram = get_ngram(line, cdict)

        if not ngram:
            continue

        # stop we find this ngram in the db already
        if find_one(ngram, db):
            # if `force`, we will iterate over all docs, but will ignore the ones that are already inserted
            if args.force:
                print '- ({0}) Ngram [{1}] already in the db, jumping to the next one...'.format(filename, ngram)
                sys.stdout.flush()
                continue

            print '- ({0}) Ngram [{1}] already in the db, stopping the recovery!'.format(filename, ngram)
            sys.stdout.flush()
            break

        ngrams.append(ngram)
        count += 1
        if count % mod == 0:
            print '- ({0}) Inserted [{1}] ngrams into db...'.format(filename, len(ngrams) * (count / mod))
            print '- ({0}) {1} -> {2}'.format(filename, ngrams[0], ngrams[-1])
            sys.stdout.flush()
            insert_ngrams(ngrams, db)
            ngrams = []

    print '- ({0}) Inserting last [{1}] ngrams into db...'.format(filename, len(ngrams))
    sys.stdout.flush()
    insert_ngrams(ngrams, db)

    print '* Finished importing file [{0}]!'.format(filename)

def fix_db():

    print '* Executing database FIX procedure...'

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
    upcount = 0
    mod = 100

    # iterate over all docs that need fixing
    orlist = [ {'syllables': { '$exists': False} }, {'rand': { '$exists': False} }, {'type': { '$exists': False} }, {'rhyme': { '$exists': False} } ]
    ngrams = coll.find({ '$or': orlist })
    total = ngrams.count()

    for ngram in ngrams:
        upngram = False
        lastword = get_last_word(ngram)

        if 'syllables' not in ngram:
            upngram = True
            ngram['syllables'] = count_syllables(lastword, cdict)
        if 'rand' not in ngram:
            upngram = True
            ngram['rand'] = random.random()
        if 'rhyme' not in ngram:
            upngram = True
            ngram['rhyme'] = get_rhyme(lastword, cdict)

        if not upngram:
            count += 1
            continue

        update_ngram(ngram, db)

        upcount += 1
        count += 1
        if count % mod == 0:
            print '- {0} out of {1} analysed! Docs updated: {2}'.format(count, total, upcount)
            sys.stdout.flush()


    print '* Database FIX procedure finished!'

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

            # add word1
            key = 'word{0}'.format(i)
            ngram[key] = word.decode('utf-8', 'ignore')

        # add frequency
        ngram['freq'] = int(parts[0])

        # add rhyme
        ngram['rhyme'] = get_rhyme(get_last_word(ngram), cdict)

        # add random number
        ngram['rand'] = random.random()

        # add the type of the last word
        wtype = get_last_word_types(' '.join(parts[1:]))
        ngram['type'] = wtype

    except Exception as e:
        print 'ERROR while parsing ngram [{0}]! Ignoring it...'.format(line)
        print traceback.format_exc()
        sys.stdout.flush()
        return None

    return ngram


def insert_ngrams(ngrams, db):
    tries = 5

    coll = get_collection(ngrams[0], db)

    while tries:
        try:
            coll.insert_many(ngrams)
            break
        except Exception as e:
            print 'ERROR while inserting ngrams {0} to {1} into db! Trying {2} more times...'.format(ngrams[0], ngrams[-1], tries)
            print traceback.format_exc()
            sys.stdout.flush()
            time.sleep(tries * 5)
            tries -= 1

    if not tries:
        print 'ERROR while adding ngram from {0} to {1}'.format(ngrams[0], ngrams[-1])
        raise Exception('Failed to add ngrams!')


def update_ngram(ngram, db):
    tries = 5

    coll = get_collection(ngram, db)

    while tries:
        try:
            coll.update({'_id': ngram['_id'] }, ngram)
            break
        except Exception as e:
            print 'ERROR while updating ngram {0} to {1} into db! Trying {2} more times...'.format(ngram['_id'], ngram, tries)
            print traceback.format_exc()
            sys.stdout.flush()
            time.sleep(tries * 5)
            tries -= 1

    if not tries:
        print 'ERROR while adding ngram from {0} to {1}'.format(ngram['_id'], ngram)
        raise Exception('Failed to update ngram!')

def create_collections(db):

    if not args.split:
        db['ngrams'].drop()
        db['ngrams'].create_index([( 'syllables', pym.ASCENDING ),
                                   ( 'word0', pym.ASCENDING ),
                                   ( 'word1', pym.ASCENDING )])
        return

    # create the split collections
    for i in range(2, 5):
        coll = 'n{0}grams'.format(i)
        db[coll].drop()

        idx = [( 'syllables', pym.ASCENDING ),
               ( 'word0', pym.ASCENDING ),
               ( 'word1', pym.ASCENDING ) ]

        if i >= 3:
            idx.append(( 'word2', pym.ASCENDING ))
        if i >= 4:
            idx.append(( 'word3', pym.ASCENDING ))

        db[coll].create_index(idx)

def find_one(ngram, db):
    coll = get_collection(ngram)
    return db[coll].find_one(ngram)

def get_collection(ngram, db):
    if not args.split:
        return db['ngrams']

    if 'word3' in ngram:
        return db['n4grams']
    if 'word2' in ngram:
        return db['n3grams']
    return db['n2grams']


def get_last_word_types(text):
    text = nltk.word_tokenize(text)
    posTagged = pos_tag(text)
    lastword_tag = map_tag('en-ptb', 'universal', posTagged[-1][1])

    # known types
    # ['NOUN','VERB','CONJ','PRON','ADP', 'PRT', 'DET']
    return lastword_tag

def get_last_word(ngram):
    words = [ k for k in ngram.keys() if k.find('word') == 0 ]
    words.sort()
    return ngram[words[-1]]

def count_syllables(word, cdict):
        word = word.lower()

        if word not in cdict:
                return 0
        else:
            return sum(l.isdigit() for s in cdict[word][0] for l in s)

def get_rhyme(word, cdict):

    if word not in cdict:
        return None

    phonemes = cdict[word][0]
    rhyme = ''
    for ph in reversed(phonemes):
        rhyme = '{0}{1}'.format(ph, rhyme)
        if contains_digits(ph):
            break

    if not len(rhyme):
        return None

    return rhyme

def contains_digits(d):
    return bool(re.search('\d', d))

if __name__ == '__main__':
    main()


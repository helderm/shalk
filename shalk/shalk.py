 # -*- coding: utf-8 -*-
import os
import random
import pymongo as pym
import tornado.ioloop
from tornado.options import define, options
from tornado.web import Application, RequestHandler


class NgramsHandler(RequestHandler):

    def initialize(self, db):
        self.db = db

    def get(self):
        # optional query string arg
        #freq = self.get_argument('freq', None)

        # required query string arg
        #word0 = self.get_argument('word0')

        #query = { 'word0': word0 }
        #if freq:
        #    query['freq'] = freq

        # query the database
        ngram = self.db['ngrams'].find_one()

        self.write('ngrams = {0}'.format(ngram))
        
#Utility function for weighted sampling        
def weightedChoice(choices):
    total = sum(w for c, w in choices)
    r = random.uniform(0, total)
    upto = 0
    for c, w in choices:
        if upto + w > r:
            return c
        upto += w
    assert False, "Shouldn't get here"
    
#Abstraction of the repeated code in nextWord       
def weightedTuples(listOfNGrams, minLength, key):
    tuples = []
    for item in listOfNGrams:
        tuple = []
        if (len(item) > minLength):
            tuple.append(item[key])
            tuple.append(item[u'freq'])
            tuples.append(tuple)
    return tuples

#This is our ngram generating function. It assumes at least two words in the input.    
def nextWord(text, db):
    words = text.split(" ")
    N = len(words)
    
    #First try 4 and 3 grams
    if(N >= 3):
        #First we attempt generating a word from the 4 gram corpus
        possible4grams = list(db['ngrams'].find({"word0" : words[N-3], "word1" : words[N-2], "word2" : words[N-1]}))
        #This executes if there is any data with "word0, word1, word2" as attributes, makes a weighted list of the word3's and returns
        #a weighted sample
        if len(possible4grams) > 0:
            tuples = weightedTuples(possible4grams, 5, u'word3')
            if(len(tuples) > 0):
                 return weightedChoice(tuples)
        #If we haven't returned yet, that means that no possible 4 gram was returned. The if condition guarantees us to return a 3gram here, however.
            possible3grams = list(db['ngrams'].find({"word0" : words[N-2], "word1" : words[N-1]}))
            tuples = weightedTuples(possible3grams, 4, u'word2')
            if(len(tuples) > 0):
                 return weightedChoice(tuples)
    #Then we try 3 and 2 grams
    if(N>=2):
        possible3grams = list(db['ngrams'].find({"word0" : words[N-2], "word1" : words[N-1]}))
        tuples = weightedTuples(possible3grams, 4, u'word2')
        if len(possible3grams) > 0:
            tuples = []
            if(len(tuples) > 0):
                 return weightedChoice(tuples)
            possible2grams = list(db['ngrams'].find({"word0" : words[N-1]}))
            tuples = weightedTuples(possible2grams, 3, u'word1')
            if(len(tuples) > 0):
                 return weightedChoice(tuples)
    #If we've reached this point, no 2 grams are available. We generate a random word:
    return "random"

def main():
    define("host", default="127.0.0.1", help="Host IP")
    define("port", default=9999, help="Port")
    tornado.options.parse_command_line()

    # init database connection
    client = pym.MongoClient()
    db = client['shalk']
    text = "the ghost of"
    for x in range(0, 20):
        text += " " + nextWord(text, db)
        print text

    application = Application([(r"/ngrams/find", NgramsHandler, dict(db=db)),])

    application.listen(options.port, options.host)
    tornado.ioloop.IOLoop.instance().start()


if __name__ == "__main__":
    main()


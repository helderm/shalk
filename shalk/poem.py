import poem_template as pt
import random

def Poem(object):

    def __init__(self, db, pattern):
        self.db = db
        self.pattern = pattern
        self.template = pt.PoemTemplate(pattern, [])

    def generate(self):
        template = self.template.createTemplate()

        syllables = [ i for x in template for i in x ]

        text = ''
        for syl in syllables:
            text += self.next_word(text, self.db, syl)
		return text

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

	#This is our ngram generating function. 
	def nextWord(text, db):
		words = text.split(" ")
		N = len(words)
		
		#First try 4 and 3 grams
		if(N >= 3):
			#First we attempt generating a word from the 4 gram corpus
			possible4grams = list(db['ngrams'].find({"word0" : words[N-3], "word1" : words[N-2], "word2" : words[N-1], "syllables" = syl}))
			#This executes if there is any data with "word0, word1, word2" as attributes, makes a weighted list of the word3's and returns
			#a weighted sample
			if len(possible4grams) > 0:
				tuples = weightedTuples(possible4grams, 5, u'word3')
				if(len(tuples) > 0):
					 return weightedChoice(tuples)
			#If we haven't returned yet, that means that no possible 4 gram was returned. The if condition guarantees us to return a 3gram here, however.
				possible3grams = list(db['ngrams'].find({"word0" : words[N-2], "word1" : words[N-1], "syllables" = syl}))
				tuples = weightedTuples(possible3grams, 4, u'word2')
				if(len(tuples) > 0):
					 return weightedChoice(tuples)
		#Then we try 3 and 2 grams
		if(N>=2):
			possible3grams = list(db['ngrams'].find({"word0" : words[N-2], "word1" : words[N-1], "syllables" = syl}))
			tuples = weightedTuples(possible3grams, 4, u'word2')
			if len(possible3grams) > 0:
				if(len(tuples) > 0):
					 return weightedChoice(tuples)
				possible2grams = list(db['ngrams'].find({"word0" : words[N-1], "syllables" = syl}))
				tuples = weightedTuples(possible2grams, 3, u'word1')
				if(len(tuples) > 0):
					 return weightedChoice(tuples)
		if(N>=1):
			possible2grams = list(db['ngrams'].find({"word0" : words[N-1], "syllables" = syl}))
			tuples = weightedTuples(possible2grams, 3, u'word1')
			if len(possible2grams) > 0:
				if(len(tuples) > 0):
					 return weightedChoice(tuples)
				possible1grams = list(db['ngrams'].find({"syllables" = syl}))
				tuples = weightedTuples(possible2grams, 3, u'word1')
				if(len(tuples) > 0):
					 return weightedChoice(tuples)
					 
		possible1grams = list(db['ngrams'].find({"syllables" = syl}))
		tuples = weightedTuples(possible4grams, 5, u'word3')
			if(len(tuples) > 0):
				 return weightedChoice(tuples)
		#If we've reached this point, everything failed:
		return "random"



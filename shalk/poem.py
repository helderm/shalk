import poem_template as pt

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
            text += self.next_word(text, syl)



    def next_word(self):
        pass



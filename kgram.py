class KGramIndex(object):
    """Pydoc inc, going to work on this a lot more but base functionality is here"""
    def __init__(self, num_grams):
        self.num_grams = num_grams
        self.index = {}

    """Maps word to kgrams"""
    def map_ngram(self, word):
        grams = zip(*[word[i:] for i in range(self.num_grams)])
        for gram in grams:
            gram_str = ''.join(gram)
            if gram_str not in self.index:
                self.index[gram_str] = [word]
            elif word not in self.index[gram_str]:
                self.index[gram_str].append(word)

    """Iterates through input list to construct kgrams"""
    def index_list(self, input_list):
        for word in input_list:
            self.map_ngram(word)

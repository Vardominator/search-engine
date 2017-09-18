"""KGramIndex class file"""

class KGramIndex(object):
    """Pydoc inc, going to work on this a lot more but base functionality is here"""
    def __init__(self, num_grams):
        self.num_grams = num_grams
        self.index = {}

    def map_ngram(self, word):
        """Maps word to kgrams"""
        grams = zip(*[word[i:] for i in range(self.num_grams)])
        for gram in grams:
            gram_str = ''.join(gram)
            if gram_str not in self.index:
                self.index[gram_str] = [word]
            elif word not in self.index[gram_str]:
                self.index[gram_str].append(word)

    def add_to_index(self, input_list):
        """Iterates through input list to construct kgram index"""
        if input_list:
            for word in input_list:
                self.map_ngram(word)
        else:
            print('Empty list passed to kgram parser.')

    def get_words(self, gram):
        """Returns a list of all words found containing kgram from index"""
        if gram in self.index:
            return self.index[gram]
        else:
            print("Key not found in kgram index.")
            return None

    @staticmethod
    def print_kgrams(kgram_number, word):
        """Helper function to list kgrams for individual words"""
        grams = set(zip(*[word[i:] for i in range(kgram_number)]))
        print('{}-Grams found in {}:'.format(kgram_number, word))
        for gram in grams:
            print(''.join(gram))

from itertools import chain
from collections import defaultdict

class KGramIndex(object):
    """KGram Index that builds dictionaries of grams up to the designated
       number of grams. Each word added to the index is broken into grams
       from 1 to num_grams, and is added to the list for each gram. The
       index includes functions to retrieve words containing each of a
       list of grams."""

    def __init__(self, num_grams, vocab = None):
        self.num_grams = num_grams
        self.index = defaultdict(list)
        if vocab:
            self.add_to_index(vocab)

    def map_ngram(self, word):
        """Maps word to kgrams from 1 to k"""
        gram_word = "$" + word + "$"
        grams = map(set, [zip(*[gram_word[i:] for i in range(num_grams)]) for num_grams in range(1, self.num_grams+1)])
        for gram_set in grams:
            for gram in gram_set:
                gram_str = ''.join(gram)
                self.index[gram_str].append(word)

    def add_to_index(self, input_list):
        """Iterates through input list to construct kgram index"""
        if input_list:
            for word in input_list:
                self.map_ngram(word)
        else:
            print('Empty list passed to kgram parser.')

    def get_words(self, gram):
        """Returns a list of all words found containing kgram from index.
           Ensure that grams include '$' symbol"""
        if gram in self.index:
            return self.index[gram]
        else:
            print("Key not found in kgram index: {}".format(gram))
            return []

    def get_intersection_grams(self, grams):
        """Gets words that share the grams in common."""
        # Get a set of grams that are the correct size by either returning a gram or splitting it
        grams = set(chain(*[self.split_gram(gram) for gram in grams]))
        gram_sets = []
        for gram in grams:
            gram_sets.append(set(self.get_words(gram)))
        return set.intersection(*gram_sets)

    def split_gram(self, gram):
        """Splits a gram that is too long by returning a list of the largest subgrams"""
        if len(gram) <= self.num_grams:
            return [gram]
        max_len = self.num_grams
        return [gram[ind:ind+(max_len)] for ind in range(0, len(gram) - max_len + 1, 1)]

    @staticmethod
    def print_kgrams(kgram_number, word):
        """Helper function to list kgrams for individual words"""
        gram_word = "$" + word + "$"
        grams = set(zip(*[gram_word[i:] for i in range(kgram_number)]))
        print('{}-Grams found in {}:'.format(kgram_number, word))
        for gram in grams:
            print(''.join(gram))
